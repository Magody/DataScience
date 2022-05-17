import os

from numpy.lib.function_base import average
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

from models.ChatbotRetrieval import ChatbotRetrieval
import random
import json
import pickle
import numpy as np
import sys
from datetime import datetime, date
import matplotlib.pyplot as plt

from tensorflow.keras.models import load_model

from flask import Flask, request, jsonify


from tensorflow.keras.optimizers import SGD, Adam

from models.db.MongoDatabase import MongoDatabase
from models.util.data_preparation import *
from models.util.mongo_util import *


# python train.py chatbot_test test brain_telegram cb_faq_firma 1 true

arg_list = sys.argv
# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(arg_list))

Config.setEnvironment(os.path.join(".env.json"))

db_name = arg_list[1]
user = arg_list[2]
brain_name = arg_list[3]
chatbot_name = arg_list[4]
verbose = int(arg_list[5])
evaluate_weakness = arg_list[6].lower() == "true"


# mongoDatabase = MongoDatabase(db_name, "mongodb://%s:%s@%s:%d" % (Config.MONGODB_USER, Config.MONGODB_PASSWORD, Config.HOST, Config.MONGO_DB_PORT))
mongoDatabase = MongoDatabase(db_name, "mongodb://localhost:27017")   

brain = mongoDatabase.find("brains", {"user": user, "name": brain_name})
chatbots = brain.get("chatbots", None)

path_brain_flow = os.path.join("chatbots", "brain_flow")

tree_broker = brain["config"]["tree_broker"]

generateConcatsFromArrays(path_brain_flow, tree_broker, chatbots, verbose-1)


chatbots_with_special_patterns: dict = fillAgentsPatterns(path_brain_flow, chatbots, verbose-1)

history_scores = {}


ChatbotRetrieval.save_path = os.path.join("chatbots", "models_saved")

history_test_lose = []
history_test_acc = []
history_train_lose = []
history_train_acc = []
history_val_lose = []
history_val_acc = []

for key, document_chatbot in chatbots_with_special_patterns.items():


    if key == "human":
        continue

    if chatbot_name != "all" and chatbot_name != key:
        continue

    if verbose > 0:
        print("training", key)
    
    chatbot: ChatbotRetrieval = ChatbotRetrieval.convertDocumentToChatbotRetrieval(brain_name, key, document_chatbot)
    
    # chatbot.epochs = 50
    # chatbot.batch_size = 4
    history, acc_test = chatbot.train(porc_train=1, porc_val=0, verbose=(verbose-1))
    # print(verbose, "verbose", type(verbose))
    
    history_train_loss = history['loss']
    history_train_categorical_accuracy = history['categorical_accuracy']
    history_val_loss = history['val_loss']
    history_val_categorical_accuracy = history['val_categorical_accuracy']


    history_test_lose.append(acc_test[0])
    history_test_acc.append(acc_test[1])
    history_train_lose.append(history_train_loss[-1])
    history_train_acc.append(history_train_categorical_accuracy[-1])
    history_val_lose.append(history_val_loss[-1])
    history_val_acc.append(history_val_categorical_accuracy[-1])
    
    """
    plt.show()
    plt.grid(True)
   
    """

    if evaluate_weakness:

        
        if verbose > 0:
            print("Evaluating weakness")

        scores = chatbot.evaluateWeakness(verbose-1)
        print(key, scores)
        history_scores[key] = scores

    if verbose > 0:
        #print(history)
        plt.figure(key)
        plt.subplot(1, 2, 1)
        plt.plot(range(1, chatbot.epochs+1), history_train_loss, label="Train loss")
        plt.plot(range(1, chatbot.epochs+1), history_val_loss, label="Val loss")
        plt.xlabel('epochs')
        plt.ylabel('loss')
        plt.title('Loss')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(range(1, chatbot.epochs+1), history_train_categorical_accuracy, label="Train accuracy")
        plt.plot(range(1, chatbot.epochs+1), history_val_categorical_accuracy, label="Val accuracy")
        plt.xlabel('epochs')
        plt.ylabel('accuracy')
        plt.title('Categorical accuracy')
        plt.legend()


        # datetime object containing current date and time
        now = datetime.now()

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")

        plt.savefig(os.path.join(ChatbotRetrieval.save_path, brain_name, key, f"summary_{dt_string}.png"))
        

        

if verbose > 0:
    print("\n\n", history_scores)



print("*****")
train_acc = round(average(history_train_acc)*100, 2)
test_acc = round(average(history_test_acc)*100, 2)
val_acc = round(average(history_val_acc)*100, 2)
# print(f"Error medio: {average(history_test_lose)}")
print(f"Accuracy medio: {train_acc} %")
# print(f"Accuracy final: {history_test_acc[-1]}")
