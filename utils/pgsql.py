from psycopg2.extensions import connection, cursor
import psycopg2
from configparser import ConfigParser
from typing import List, Dict

class Query():
    def __init__(self) -> None:
        self._connect()
        
    def _config(self, filename='config.ini', section='postgresql'):
        parser = ConfigParser()
        parser.read(filename)
        
        db = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))
        
        return db

    def _connect(self):
        conn = None
        try:
            params = self._config()
            
            print("Connecting to PostgreSQL database...")
            conn: connection = psycopg2.connect(**params)
            cur: cursor = conn.cursor()
            
            print('PostgreSQL database version: ')
            cur.execute('SELECT version()')
            
            db_version = cur.fetchone()
            print(db_version)
            
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        if conn is not None:
            self.conn = conn
    
    def add_guild(self, guild_id, guild_name):
        """Adds guild to main guild table along with creating a independent guild table

        Args:
            guild_id (int): the guilds id given by discord
            guild_name (str): The name of the guild
        """
        
        sql = """
        create table if not exists Guilds(
            GuildID varchar(50),
            GuildName varchar(255)
        );
        insert into Guilds(GuildID, GuildName) values (%s, %s);
        
        create table if not exists Guild%s(MemberID varchar(100), GuildMember json, Balance numeric(65, 2), Items json);
        
        """
        cur = self.conn.cursor()
        
        cur.execute(sql, (guild_id, guild_name, guild_id,))
        
        self.conn.commit()
        cur.close()
        
    def add_user(self, guild_id, user_id, user, balance, items):
        """Add user to guild database

        Args:
            guild_id (str): The guild to add the user to
            user (DiscordUser): The user to add
            balance (decimal): The users balance for the guild
            items (Dict): The users items within the guild
        """
        
        sql = """
        insert into Guild%s(MemberID, GuildMember, Balance, Items) values(%s, %s, %s, %s) returning GuildMember;
        """
        cur = self.conn.cursor()
        
        cur.execute(sql, (guild_id, user_id, user, balance, items,))
        
        self.conn.commit()
        cur.close()
        
    def get_user(self, guild_id: str, user_id: str):
        sql = """
        select MemberID, GuildMember, Balance, Items 
        from Guild%s 
        where MemberID = cast(%s as varchar(100));
        """
        
        cur = self.conn.cursor()
        cur.execute(sql, (guild_id, user_id,))
        result = cur.fetchone()
        print(result)
        return result
    
    def get_balance(self, guild_id, user_id):
        sql = """
        select Balance from Guild%s where MemberID = cast(%s as varchar(100));
        """
        cur = self.conn.cursor()
        cur.execute(sql, (guild_id, user_id,))
        result = cur.fetchone()
        print(result)
        return result
    
    def update_user(self, guild_id, user_id, userdata: Dict[List[Dict]]):
        """Update a user within the database

        Args:
            guild_id (:class:`str`): The id for the guild the user is in
            user_id (:class:`str`): The unique id for the user within discord
            userdata (:class:`Dict`): the data to be updated
        """
        
        sql = """
        UPDATE Guild%s
        SET Balance = %s,
            Items = %s
        WHERE MemberID = %s
        """
        cur = self.conn.cursor()
        
        cur.execute(sql, (guild_id, userdata['balance'], userdata['items'],))