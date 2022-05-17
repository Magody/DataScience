
import os
from ..Monitor.UserMonitor import UserMonitor

from ..db.MongoDatabase import *
import re

from ..util.data_preparation import *
from ..util.mongo_util import *
"""
path_folder_brain_flow = os.path.join("chatbots", "brain_flow")
mongoDatabase = MongoDatabase("chatbot_test", "mongodb://%s:%s@zeus.ridetel.com:27018" % ("mongoadmin", "B0t.2021"))
responses = getChatbotsResponses(mongoDatabase, 1)
"""
from ..Monitor.GeneralMonitor import GeneralMonitor
from ..Conversation import *

def test_monitor(user, brain_name, db_name):


    Config.TIME_SECONDS_WAIT_FOR_FREE_MEMORY = 10
    Config.TIME_SECONDS_WAIT_FOR_USER_MONITOR_FREE_MEMORY = 10
    Config.TIME_SECONDS_WAIT_BASE_THREAD = 5
    Config.TIME_MINUTES_BOT_WAIT_TO_RESET = 1


    mongoDatabase =  MongoDatabase(db_name, "mongodb://%s:%s@zeus.ridetel.com:27018" % ("mongoadmin", "B0t.2021"))


    try:
        GeneralMonitor.init()

        type = "text"
        message = "servidor jurídico"
        mobile = "+593978654041"
        user = user

        others = dict()
        # others["updater"] = updater
        # ensure brain is passed by reference
        GeneralMonitor.addMessageToUserMonitor(user, brain_name, mobile, message, others, mongoDatabase, type)
        time.sleep(5)
        GeneralMonitor.addMessageToUserMonitor(user, brain_name, mobile, "Message sorpresa", others, mongoDatabase, type)
        GeneralMonitor.addMessageToUserMonitor(user, brain_name, "+593978654042", "Message otro dos", others, mongoDatabase, type)
        time.sleep(5)
        GeneralMonitor.addMessageToUserMonitor(user, brain_name, "+593978654042", "dos t1", others, mongoDatabase, type)
        GeneralMonitor.addMessageToUserMonitor(user, brain_name, "+593978654042", "dos t2", others, mongoDatabase, type)
        
        time.sleep(20)
    finally:
        GeneralMonitor.die()
        while GeneralMonitor.existMessagesToProcess():
            print("waiting for all messages to be processed")
            time.sleep(10)

        print("Waiting for threads to finish")
        threads_to_wait = []
        for username, user_monitor_value in GeneralMonitor.users_monitors.items():
            userMonitor: UserMonitor = user_monitor_value["user_monitor"]
            for brain_name, brain_value in userMonitor.brain_conversations.items():

                for unique_id, conv in brain_value["conversations"]:
                    conversation: Conversation = conv
                    threads_to_wait.append(conversation.thread)


        for thread in threads_to_wait:
            if thread:
                print("waiting for", unique_id)
                thread.join()
        print("End of program")
