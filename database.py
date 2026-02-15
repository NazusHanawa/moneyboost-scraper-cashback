import libsql

from utils import timer

class DB:
    def __init__(self, database_url, auth_token):
        self.database_url = database_url
        self.auth_token = auth_token
        self.connection = libsql.connect(database=database_url, auth_token=auth_token)
        self.cursor = self.connection.cursor()

    def commit(self):
        self.connection.commit()

    @timer
    def get_partnerships(self):
        result = self.cursor.execute("SELECT * FROM vw_partnerships")
        
        columns = [column[0] for column in result.description]
        
        rows = result.fetchall()

        partnerships = {}
        for row in rows:
            partnership_data = dict(zip(columns, row))
            
            partnership_id = partnership_data["partnership_id"]
            partnerships[partnership_id] = partnership_data
        
        return partnerships
    
    @timer
    def get_last_cashbacks(self):
        result = self.cursor.execute("SELECT partnership_id, global_value, max_value FROM vw_latest_cashbacks")
        
        columns = [column[0] for column in result.description]
        
        rows = result.fetchall()

        cashbacks = {}
        for row in rows:
            cashback_data = dict(zip(columns, row))
            
            partnership_id = cashback_data["partnership_id"]
            cashbacks[partnership_id] = cashback_data
        
        return cashbacks

    @timer
    def add_cashbacks(self, cashbacks):
        base_query = "INSERT OR IGNORE INTO cashbacks (partnership_id, global_value, max_value, description) VALUES "
        placeholders = ", ".join(["(?, ?, ?, ?)"] * len(cashbacks))
        full_query = base_query + placeholders
        
        flattened_values = []
        for cashback in cashbacks:
            row = [
                cashback["partnership_id"],
                cashback["global_value"], 
                cashback["max_value"], 
                cashback["description"]
            ]
            flattened_values.extend(row)
        
        self.cursor.execute(full_query, flattened_values)
        self.commit()

    @timer
    def update_old_cashbacks_date_end(self, partnership_ids):
        ids = list(partnership_ids)
        placeholders = ", ".join(["?"] * len(ids))

        query = f"""
        UPDATE cashbacks
        SET date_end = datetime('now', 'localtime')
        WHERE id IN (
            SELECT cashback_id
            FROM vw_latest_cashbacks
            WHERE partnership_id IN ({placeholders})
            AND (julianday('now', 'localtime') - julianday(date_end)) * 24 <= 12
        );
        """
        
        self.cursor.execute(query, ids)
        self.connection.commit()
