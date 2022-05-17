from models.tests.test_monitor import test_monitor
from models.tests.test_individual_model import test_individual_model
from models.db.MongoDatabase import *
from models.tests.test_brain import test_brain
import copy
import sys
import json
import os
from models.Config import Config
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


# brain: python test.py brain brain_walichat
# individual: python test.py individual brain_telegram
arg_list = sys.argv
print('Number of arguments:', len(sys.argv), 'arguments.')
print('Argument List:', str(arg_list))

test_type = arg_list[1]
brain_name = arg_list[2]

Config.setEnvironment(os.path.join(".env.json"))


path_brain_flow = os.path.join("chatbots", "brain_flow")
path_models_saved = os.path.join("chatbots", "models_saved")

collection_name_conversations = "conversations"
# mongoDatabase = MongoDatabase(Config.DB_NAME, "mongodb://%s:%s@%s:%d" % (Config.MONGODB_USER, Config.MONGODB_PASSWORD, Config.HOST, Config.MONGO_DB_PORT))
mongoDatabase = MongoDatabase(Config.DB_NAME, "mongodb://%s:%d" % (Config.HOST, Config.MONGO_DB_PORT))


brain = mongoDatabase.find("brains", {"user": Config.USERNAME, "name": brain_name})
chatbots = brain.get("chatbots", None)


if test_type == "brain":
    test_brain(collection_name_conversations,
               mongoDatabase, brain_name, chatbots)
elif test_type == "individual":
    chatbot_name = arg_list[3]
    test_individual_model(mongoDatabase, chatbots, brain_name, chatbot_name)
elif test_type == "monitor":
    test_monitor(brain_name)
else:
    print(test_type, "not exist")
