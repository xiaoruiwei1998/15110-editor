from abc import ABC, abstractmethod

class LLM(ABC):
  
  def _init_model(self): pass
  def _setup_mdoel(self): pass
  def get_model(self): pass
  def _format_conversation_log(self): pass
  def generate_conversation_name(self, chatlog: str): pass
  def set_up_conversation(self, chatlog: str): pass
  def predict(self, user_message: str): pass
  async def async_predict(self, user_message: str): pass
  def _format_conversation_log(self): pass
  def create_chatlog(self, cid, chatlog, is_user, time, delta): pass