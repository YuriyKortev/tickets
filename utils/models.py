from neomodel import (config, StructuredNode, StringProperty, IntegerProperty, BooleanProperty,
                      RelationshipTo, DateTimeProperty, StructuredRel, One, ZeroOrMore,
                      RelationshipFrom, DoesNotExist, DateProperty, db, clear_neo4j_database)

from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from app import app, login_manager
from datetime import timedelta, date, datetime


config.DATABASE_URL = 'bolt://neo4j:123145@localhost:7687'
#config.DATABASE_URL = 'bolt://neo4j:test@neo4j:7687'
config.AUTO_INSTALL_LABELS = True

# today = datetime.now().date()
today = date(year=2020, month=12, day=6)
week_start = today - timedelta(days=today.weekday())
week_end = week_start + timedelta(days=6)


def generate_export():

    res, cols = db.cypher_query('''
          CALL apoc.export.csv.all(null, {stream:true})
          YIELD file, nodes, relationships, properties, data
          RETURN file, nodes, relationships, properties, data
     ''')
    with open('files/db.csv', 'w', encoding='utf-8') as f:
        print(res[0][4], file=f)


def import_from_csv(some_args=None):
    clear_neo4j_database(db)
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Air_class.csv' as row
                        create (:Air_class{id: toInteger(row._id), class_type:row.class_type, price: toInteger(row.price), seats: toInteger(row.seats)})
            ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Air_flight.csv' as row
                        create (:Air_flight{id: toInteger(row._id)})
             ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Airport.csv' as row
                        create (:Airport{id: toInteger(row._id), name:row.name})
             ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/City.csv' as row
                        create (:City{id: toInteger(row._id), name:row.name})
             ''')

    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Person.csv' as row
                        create (:Person{id: toInteger(row._id), email:row.email, is_admin:toBoolean(row.is_admin), name:row.name, password_hash: row.password_hash, phone_number: row.phone_number})
             ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Station.csv' as row
                        create (:Station{id: toInteger(row._id), name:row.name})
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Train_class.csv' as row
                        create (:Train_class{id: toInteger(row._id), class_type:row.class_type, price:toInteger(row.price), seats: toInteger(row.seats)})
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/Train_ride.csv' as row
                        create (:Train_ride{id: toInteger(row._id)})
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/CLASS.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:CLASS]->(end)
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/FROM.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:FROM{time: datetime(row.time)}]->(end)
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/LOCATED.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:LOCATED]->(end)
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/REGISTERED_ON.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:REGISTERED_ON{buy_date: date(row.buy_date)}]->(end)
                 ''')
    db.cypher_query('''
                    load csv with headers from 'http://server:5000/uploads/TO.csv' as row
                        match (st) where st.id = toInteger(row._start)
                        match (end) where end.id = toInteger(row._end)
                        create (st)-[:TO{time: datetime(row.time)}]->(end)
                 ''')

    return True


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)


class Dtime(StructuredRel):
    date_time = DateTimeProperty()


class Date_rel(StructuredRel):
    buy_date = DateProperty()


class City(StructuredNode):
    name = StringProperty()
    stations = RelationshipFrom('Station', 'LOCATED')
    airports = RelationshipFrom('Airport', 'LOCATED')

    def ways_to(self, city, class_types, ride_type):
        query = f'''
                    match path = (ct1:City{{name:'{self.name}'}})<-[:LOCATED]-(:{ride_type.station_type})-[*]->(:{ride_type.station_type})-[:LOCATED]->(ct2:City{{name:'{city}'}})
                    with [x in nodes(path) where x:{ride_type.__name__}] as ns
                    return ns
                '''
        results, columns = self.cypher(query)
        paths = []
        for result in results:
            for class_type in class_types:
                path = []
                for res in result[0]:
                    ride = ride_type.inflate(res)
                    seat_class = ride.get_class(class_type)

                    node = SeatType.get_ticket(ride, seat_class)

                    path.append(node)
                paths.append(path)
        return paths


class Airport(StructuredNode):
    name = StringProperty()

    located = RelationshipTo(City, 'LOCATED', cardinality=One)


class Ride(object):
    def arrived(self):
        query = f'''
                        match (x:{self.__class__.__name__})-[r:TO]->() where ID(x)={self.id}
                        return r.time
                    '''
        results, columns = self.cypher(query)

        return results[0][0]

    def departure(self):
        query = f'''
                    match (x:{self.__class__.__name__})<-[r:FROM]-() where ID(x)={self.id}
                    return r.time
                '''
        results, columns = self.cypher(query)

        return results[0][0]

    @classmethod
    def get_ride_stats(cls, city_from, city_to, dt_from):
        query = f'''
                    match (:City{{name:'{city_from}'}})<-[:LOCATED]-(:{cls.station_type})-[f:FROM]->(ride)-[:TO]->(:{cls.station_type})-[:LOCATED]->(:City{{name:'{city_to}'}}) where date(f.time)=date('{dt_from}')
                    match (class)<-[:CLASS]-(ride)
                    return sum(class.seats)
                '''
        results, columns = db.cypher_query(query)
        all_seats = results[0][0]

        query = f'''
                    match (:City{{name:'{city_from}'}})<-[:LOCATED]-(:{cls.station_type})-[f:FROM]->(ride)-[:TO]->(:{cls.station_type})-[:LOCATED]->(:City{{name:'{city_to}'}}) where date(f.time)=date('{dt_from}')
                    match (class)<-[:CLASS]-(ride)
                    match (:Person)-[r:REGISTERED_ON]->(class)
                    return count(r)
                '''
        results, columns = db.cypher_query(query)
        bought = results[0][0]

        return bought, all_seats-bought

    @classmethod
    def create_ride(cls, station_from, station_to, dt_from, dt_to):
        query = f'''
                            match (c1:{cls.station_type}{{name:'{station_from}'}})
                            match (c2:{cls.station_type}{{name:'{station_to}'}})
                            create (c1)-[:FROM{{time:datetime('{str(dt_from).replace(' ','T')}')}}]->(ride:{cls.__name__})-[:TO{{time:datetime('{str(dt_to).replace(' ','T')}')}}]->(c2)
                            create (:{cls.ticket_class.__name__}{{class_type:'{cls.ticket_class.types[0]['name']}', price:{cls.ticket_class.types[0]['price']}, seats:{cls.ticket_class.types[0]['seats']} }})<-[:CLASS]-(ride)
                            create (:{cls.ticket_class.__name__}{{class_type:'{cls.ticket_class.types[1]['name']}', price:{cls.ticket_class.types[1]['price']}, seats:{cls.ticket_class.types[1]['seats']} }})<-[:CLASS]-(ride)
                            create (:{cls.ticket_class.__name__}{{class_type:'{cls.ticket_class.types[2]['name']}', price:{cls.ticket_class.types[2]['price']}, seats:{cls.ticket_class.types[2]['seats']} }})<-[:CLASS]-(ride)
                        '''
        print(query)
        db.cypher_query(query)
        return 'True'


class SeatType(object):
    class_type = StringProperty()
    price = IntegerProperty()
    seats = IntegerProperty()

    def get_ride(self):
        query = f'''
                    match (n:{self.__class__.__name__}) where ID(n)={self.id}
                    match (ride)-[:CLASS]->(n)
                    return ride
                '''
        results, columns = db.cypher_query(query)
        if results:
            return results[0][0]
        else:
            raise DoesNotExist

    def num_of_free_seats(self):
        query = f'''
                    match (n) where ID(n)={self.id}
                    match (p:Person)-[:REGISTERED_ON]->(n)
                    return n.seats - count(p)
                '''
        results, columns = db.cypher_query(query)
        if not results:
            return self.seats
        return results[0][0]

    @classmethod
    def get_num_of_sold_tickets_by_date(cls, buy_date):
        query = f'''
                    match (:Person)-[r:REGISTERED_ON{{buy_date:date('{buy_date}')}}]->(:{cls.__name__})
                    return count(r)
                '''
        results, columns = db.cypher_query(query)
        if not results:
            return 0
        return results[0][0]

    @classmethod
    def get_num_of_sold_tickets_in_date_range(cls, start_date, end_date):
        counts = []
        for date_x in date_range(start_date, end_date):
            counts.append(cls.get_num_of_sold_tickets_by_date(date_x))
        return counts

    @classmethod
    def get_num_of_sold_tickets_today(cls):
        # today = datetime.now().date()
        today = date(year=2020, month=11, day=30)
        return cls.get_num_of_sold_tickets_by_date(today)

    @classmethod
    def get_num_of_sold_tickets_on_current_week(cls):
        return cls.get_num_of_sold_tickets_in_date_range(week_start, week_end)

    @classmethod
    def get_ticket_class_by_id(cls, node_id):
        query = f'''
                    match (n:{cls.__name__}) where ID(n)={node_id} return n
                '''
        results, columns = db.cypher_query(query)
        if results:
            return cls.inflate(results[0][0])
        else:
            raise DoesNotExist

    @classmethod
    def get_list_of_air_classes(cls, list_of_node_id):
        return [cls.get_ticket_class_by_id(class_id) for class_id in list_of_node_id]

    @classmethod
    def get_most_popular_ticket(cls):
        query = f'''
                    match (n:{cls.__name__})<-[r:REGISTERED_ON]-(p:Person)
                    with n,r,p, count(r) as nums order by nums
                    return n
                    limit 1
                '''
        results, columns = db.cypher_query(query)
        if results:
            seat_class = cls.inflate(results[0][0])

            try:
                ride = seat_class.get_ride()
            except DoesNotExist:
                return None

            return cls.get_ticket(ride, seat_class)
        else:
            return None

    @staticmethod
    def get_ticket(ride_type, seat_class):
        ticket = {
            'af_id': ride_type.id,
            'class_title': seat_class.class_type,
            'free_seats': seat_class.num_of_free_seats(),
            'class_id': seat_class.id,
            'price': seat_class.price,
            'ap_from': ride_type.from_.single().name,
            'ap_to': ride_type.to_.single().name,
            'city_from': ride_type.from_.single().located.single().name,
            'city_to': ride_type.to_.single().located.single().name,
            'dtime_arrived': ride_type.arrived(),
            'dtime_departure': ride_type.departure(),
            'type': ride_type.ticket_type
        }
        return ticket


class Air_class(SeatType, StructuredNode):
    types = [{'name': 'Economy', 'price': 200, 'seats': 300},
             {'name': 'Business', 'price': 400, 'seats': 300},
             {'name': 'First', 'price': 800, 'seats': 300}]

    def get_ride(self):
        res = super().get_ride()
        return Air_flight.inflate(res)

    @staticmethod
    def get_tickets(list_of_node_id, user):
        tickets = []
        for class_id in list_of_node_id:
            seat_class = Air_class.get_ticket_class_by_id(class_id)
            ride = seat_class.get_ride()
            ticket = SeatType.get_ticket(ride, seat_class)

            if user.registered_air.is_connected(seat_class):
                ticket['already_bought'] = True
            else:
                ticket['already_bought'] = False

            tickets.append(ticket)

        return tickets


class Train_class(SeatType, StructuredNode):
    types = [{'name': 'Плацкарт', 'price': 200, 'seats': 300},
             {'name': 'Купэ', 'price': 300, 'seats': 300},
             {'name': 'СВ', 'price': 500, 'seats': 300}]

    def get_ride(self):
        res = super().get_ride()
        return Train_ride.inflate(res)

    @staticmethod
    def get_tickets(list_of_node_id, user):
        tickets = []
        for class_id in list_of_node_id:
            seat_class = Train_class.get_ticket_class_by_id(class_id)
            ride = seat_class.get_ride()
            ticket = SeatType.get_ticket(ride, seat_class)

            if user.registered_train.is_connected(seat_class):
                ticket['already_bought'] = True
            else:
                ticket['already_bought'] = False

            tickets.append(ticket)

        return tickets



class Air_flight(Ride, StructuredNode):
    from_ = RelationshipFrom(Airport, 'FROM', model=Dtime, cardinality=One)
    to_ = RelationshipTo(Airport, 'TO', model=Dtime, cardinality=One)
    ride_class = RelationshipTo('Air_class', 'CLASS')
    station_type = 'Airport'
    ticket_type = 'air'
    ticket_class = Air_class

    def get_class(self, class_id):
        if class_id == 1:
            return self.ride_class.get_or_none(class_type='Economy')
        elif class_id == 2:
            return self.ride_class.get_or_none(class_type='Business')
        elif class_id == 3:
            return self.ride_class.get_or_none(class_type='First')


class Train_ride(Ride, StructuredNode):
    from_ = RelationshipFrom('Station', 'FROM', model=Dtime, cardinality=One)
    to_ = RelationshipTo('Station', 'TO', model=Dtime, cardinality=One)
    ride_class = RelationshipTo('Train_class', 'CLASS')
    station_type = 'Station'
    ticket_type = 'train'
    ticket_class = Train_class

    def get_class(self, class_id):
        if class_id == 1:
            return self.ride_class.get_or_none(class_type='Купэ')
        elif class_id == 2:
            return self.ride_class.get_or_none(class_type='Плацкарт')
        elif class_id == 3:
            return self.ride_class.get_or_none(class_type='СВ')


class Person(UserMixin, StructuredNode):
    name = StringProperty()
    password_hash = StringProperty()
    email = StringProperty()
    phone_number = StringProperty()
    is_admin = BooleanProperty()

    registered_air = RelationshipTo('Air_class', 'REGISTERED_ON', cardinality=ZeroOrMore, model=Date_rel)
    registered_train = RelationshipTo('Train_class', 'REGISTERED_ON', cardinality=ZeroOrMore, model=Date_rel)

    def set_password_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def register_on_air_ticket(self, class_id):
        ac = Air_class.get_ticket_class_by_id(class_id)
        res = self.registered_air.connect(ac)
        res.buy_date = datetime.now().date()
        res.save()
        if res:
            return True
        else:
            return False

    def register_on_train_ticket(self, class_id):
        tc = Train_class.get_ticket_class_by_id(class_id)
        res = self.registered_train.connect(tc)
        res.buy_date = datetime.now().date()
        res.save()
        if res:
            return True
        else:
            return False

    @staticmethod
    def get_person_by_id(node_id):
        query = f'''
                    match (n:Person) where ID(n)={node_id} return n
                '''
        results, columns = db.cypher_query(query)
        if results:
            return Person.inflate(results[0][0])
        return None


@login_manager.user_loader
def load_user(user_id):
    return Person.get_person_by_id(user_id)


class Station(StructuredNode):
    name = StringProperty()

    located = RelationshipTo(City, 'LOCATED', cardinality=One)


def path_filter(date_time):
    def fun(path):
        if date_time is None or path[0]['dtime_departure'].date() == date_time:
            i = 0
            while i < len(path) - 1:
                if path[i]['dtime_arrived'] > path[i + 1]['dtime_departure']:
                    return False
                i += 1

            return True

        return False

    return fun


def ticket_filter(date_time):
    def fun(ticket):
        if ticket['dtime_departure'].date() == date_time:
            return True
        else:
            return False

    return fun
