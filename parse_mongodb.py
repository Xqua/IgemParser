#!/usr/bin/env python

import bson
# import pandas as pd
import sys
import os
# Opening Database

path = sys.argv[1]


def Parse_Rooms(path="rocketchat_room.bson"):
    """Parse the room file from rocket chat: rocketchat_room.bson and returns a table of the results plus a mapping of room ID and room names."""
    bson_file = open(path, 'rb')
    rooms = bson.decode_all(bson_file.read())
    # Parsing Rooms

    room = []
    rID_name = {}
    for i in rooms:
        Type = i['t']
        creation_date = i['ts'].isoformat()
        nb_msg = i['msgs']
        rID = i['_id']
        if Type != 'd':
            name = i['name']
            if name == 'general':
                creator = None
            else:
                creator = i['u']['username']
            rID_name[rID] = name
        else:
            name = None
            creator = None
        users = i['usernames']
        tmp = [str(i) for i in [rID, name, creator, creation_date, Type, nb_msg, ','.join(users)]]
        room.append(tmp)
    return room, rID_name


def Parse_Messaged(path="rocketchat_message.bson", rID_name=None):
    """Parse the message file from rocketchat db: rocketchat_message.bson and resturn a table of the results."""
    # parsing messages
    if rID_name is None:
        room, rID_name = Parse_Rooms()

    bson_file = open(path, 'rb')
    messages = bson.decode_all(bson_file.read())

    res = []

    for i in messages:
        if 'u' in i:
            if 'msg' in i:
                if 'rid' in i:
                    tmp = []
                    tmp.append(i['rid'])
                    if i['rid'] in rID_name:
                        tmp.append(rID_name[i['rid']])
                    else:
                        tmp.append('None')
                    tmp.append(i['u']['username'])
                    tmp.append(i['ts'].isoformat())
                    tmp.append(i['msg'].replace('\t', ' '))
                    res.append(tmp)
    return res

# writting results
rpath = os.path.join(path, 'rocketchat_room.bson')

res, rID_name = Parse_Rooms(path=rpath)
rLeg = ['RoomID', 'RoomName', 'RoomCreator', 'RoomCreation', 'RoomType', 'NumberOfMessages', 'RoomUsers']

f = open('rocket_chat_rooms.tsv', 'w')
f.write("\t".join(rLeg) + '\n')
for i in res:
    f.write('\t'.join(i).encode('utf8') + '\n')
f.close()


mpath = os.path.join(path, 'rocketchat_message.bson')

res = Parse_Messaged(path=mpath, rID_name=rID_name)
mLeg = ['RoomID', 'RoomName', 'User', 'timestamp', 'Message']

f = open('rocket_chat_msg.tsv', 'w')
f.write("\t".join(mLeg) + '\n')
for i in res:
    f.write('\t'.join(i).encode('utf8') + '\n')
f.close()


# def imediate():
#     bson_file = open('/home/lblondel/Documents/CommonGrounds/rocket_chat_db/test/rocketchat/rocketchat_message.bson', 'rb')
#     b = bson.decode_all(bson_file.read())

#     # f = open('rocket_chat_msg.tsv','w')

#     res = []

#     for i in b:
#         if 'u' in i:
#             if 'msg' in i:
#                 if 'rid' in i:
#                     tmp = []
#                     tmp.append(i['rid'])
#                     tmp.append(i['u']['username'])
#                     tmp.append(i['ts'])
#                     tmp.append(i['msg'])
#                     res.append(tmp)

#     df = pd.DataFrame(res, columns=['RoomID', 'User', 'timestamp', 'Message'])
#     return df
