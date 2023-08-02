from psycopg2.extensions import connection, cursor

class Query():
    def __init__(self, conn: connection) -> None:
        self.conn = conn
    
    def add_guild(self, guild_id, guild_name):
        """Adds guild to main guild table along with creating a independent guild table

        Args:
            guild_id (int): the guilds id given by discord
            guild_name (str): The name of the guild
        """
        
        sql = f"""
        create table if not exists Guilds(
            GuildID varchar(50),
            GuildName varchar(255)
        );
        insert into Guilds(GuildID, GuildName) values (%s, %s);
        
        create table if not exists Guild{guild_id}(MemberID varchar(100), GuildMember json, Balance numeric(65, 2), Items json);
        
        """
        cur = self.conn.cursor()
        
        cur.execute(sql, (guild_id, guild_name))
        
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
        
        sql = f"""
        insert into Guild{guild_id}(UserID, GuildMember, Balance, Items) values(%s, %s, %s, %s) returning GuildMember;
        """
        cur = self.conn.cursor()
        
        cur.execute(sql, (user_id, user, balance, items,))
        
        self.conn.commit()
        cur.close()
        
    def get_user(self, guild_id, user_id):
        sql = f"""
        select (GuildMember, Balance, Items) from Guild{guild_id} where UserID = {user_id};
        """
        
        cur = self.conn.cursor()
        cur.execute(sql)
        result = cur.fetchone()
        print(result)
        return result