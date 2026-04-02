# Import necessary Libraries.
from pydantic_settings import BaseSettings 
from urllib.parse import quote_plus 

# Class for the base model.
class Settings(BaseSettings): 
    mysql_host: str = "127.0.0.1"   
    mysql_port: int = 3306 
    mysql_user: str = "root" 
    mysql_password: str = "" 

    @property 
    def master_db_url(self) -> str: 
        if self.mysql_password:
            encoded_password = quote_plus(self.mysql_password)
            return f"mysql+pymysql://{self.mysql_user}:{encoded_password}@{self.mysql_host}:{self.mysql_port}/websites"
        else:
            return f"mysql+pymysql://{self.mysql_user}@{self.mysql_host}:{self.mysql_port}/websites"
    
    @property 
    def mysql_root_url(self) -> str: 
        if self.mysql_password:
            encoded_password = quote_plus(self.mysql_password)
            return f"mysql+pymysql://{self.mysql_user}:{encoded_password}@{self.mysql_host}:{self.mysql_port}/"
        else:
            return f"mysql+pymysql://{self.mysql_user}@{self.mysql_host}:{self.mysql_port}/"

settings = Settings()