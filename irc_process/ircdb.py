"""this module is to create sqlalchemy mapper for IRC database
to be created for Post-Processing"""

from sqlalchemy import Column, Integer, String, create_engine, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.sql import and_
from sqlalchemy.sql import select

BASE = declarative_base()


class SegmentedMessage(BASE):
    """model the segmented message table"""
    __tablename__ = "tbl_segmented_message"

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    segmentation_index = Column(Integer)
    timing_index = Column(Integer)
    day_index = Column(String(30))
    date_time = Column(String(30))
    sender_name = Column(String(30))
    recipient_name = Column(String(30))
    message = Column(String(800))


class SegmentedUser(BASE):
    """model the segmented user table"""
    __tablename__ = "tbl_segmented_user"

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    segmentation_index = Column(Integer)
    user1_name = Column(String(30))
    user2_name = Column(String(30))


class Message(BASE):
    """model the message table"""
    __tablename__ = 'tbl_message'

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    dialogue_id = Column(String(100))
    message = Column(String(800))


class DialogueTurns(BASE):
    """model the dialogue turns table"""
    __tablename__ = 'tbl_dialogue_turns'

    file_name = Column(String(100), primary_key=True)
    turns = Column(Integer)


# creating indices for important columns
Index('ind_p', SegmentedMessage.row_id)
Index('ind_l', SegmentedUser.row_id)
Index('ind_x', SegmentedMessage.timing_index)
Index('ind_y', SegmentedMessage.segmentation_index)
Index('ind_z', SegmentedMessage.day_index)
Index('ind_e', SegmentedUser.user1_name)
Index('ind_f', SegmentedUser.user2_name)
Index('ind_w', Message.dialogue_id)
Index('ind_q', DialogueTurns.file_name)
Index('ind_k', DialogueTurns.turns)


def setup_db():
    """create database scheme and setup the session"""
    db_engine = create_engine('sqlite:///:memory:', echo=False)
    BASE.metadata.create_all(db_engine)
    return db_engine

IRC_CONNECTION = setup_db()


def save_segmented_message(seg_index, time_index, day_index, date_time, sender,
                           recipient, message):
    """insert segmented message record into DB"""
    insert_ = SegmentedMessage.__table__.insert() \
        .values(segmentation_index=seg_index,
                timing_index=time_index,
                day_index=day_index,
                date_time=date_time,
                sender_name=sender,
                recipient_name=recipient,
                message=message)
    IRC_CONNECTION.execute(insert_)


def save_segmented_user(seg_index, user1_name, user2_name):
    """insert segmented user record into DB"""
    insert_ = SegmentedUser.__table__.insert() \
        .values(segmentation_index=seg_index,
                user1_name=user1_name,
                user2_name=user2_name)
    IRC_CONNECTION.execute(insert_)


def save_message(file_id, line):
    """insert an message with its associate file name and path"""
    insert_ = Message.__table__.insert(). \
        values(dialogue_id=file_id, message=line)
    IRC_CONNECTION.execute(insert_)


def save_dialogue_turns(file_id, turns):
    """insert a dialogue turns number with its associate file name and path"""
    insert_ = DialogueTurns.__table__.insert().values(file_name=file_id, turns=turns)
    IRC_CONNECTION.execute(insert_)


def get_message(file_id):
    """retrieve an message text from DB for a given file name"""
    query_ = select([Message.message]).where(Message.dialogue_id == file_id)
    message_text = IRC_CONNECTION.execute(query_).fetchall()
    return message_text


def get_all_messages():
    """retrieve an message text from DB for a given file name"""
    query_ = select([Message.message])
    all_messages = IRC_CONNECTION.execute(query_).fetchall()
    return all_messages


def get_usr_segmented_indices(users_pair):
    """retrieve segmentation indices from DB for a certain pair of users"""
    query_ = select([SegmentedUser.segmentation_index]). \
        where(and_(SegmentedUser.user1_name ==
                   users_pair[0],
                   SegmentedUser.user2_name ==
                   users_pair[1])).distinct()
    segmentation_indices = IRC_CONNECTION.execute(query_).fetchall()
    return segmentation_indices


def get_users_pairs():
    """retrieve a certain pair of users from DB"""
    query_ = select([SegmentedUser.user1_name,
                     SegmentedUser.user2_name]).distinct()
    pairs = IRC_CONNECTION.execute(query_).fetchall()
    return pairs


def get_segmented_message(segmentation_ids):
    """retrieve segmented message(s) from DB by a given segmentation id(s)"""
    if len(segmentation_ids) == 1:
        query_ = select([SegmentedMessage.date_time,
                         SegmentedMessage.sender_name,
                         SegmentedMessage.recipient_name,
                         SegmentedMessage.message]) \
            .where(SegmentedMessage.segmentation_index
                   == segmentation_ids[0]) \
            .order_by(SegmentedMessage.timing_index).distinct()
        dialogues = IRC_CONNECTION.execute(query_).fetchall()

    else:
        query_ = select([SegmentedMessage.date_time,
                         SegmentedMessage.sender_name,
                         SegmentedMessage.recipient_name,
                         SegmentedMessage.message]) \
            .where(SegmentedMessage.segmentation_index.in_(tuple(segmentation_ids))) \
            .order_by(SegmentedMessage.timing_index).distinct()
        dialogues = IRC_CONNECTION.execute(query_).fetchall()
    return dialogues


def get_msg_segmented_indices(day_index_p, indices_p):
    """retrieve from DB a distinct list of messages segmentation ids for a given day """
    seg_indices = []
    if len(indices_p) == 1:
        query_ = select([SegmentedMessage.segmentation_index]). \
            where(and_(SegmentedMessage.day_index == day_index_p,
                       SegmentedMessage.segmentation_index == indices_p[0])).distinct()
        seg_indices = IRC_CONNECTION.execute(query_).fetchall()

    elif len(indices_p) > 1:
        query_ = select([SegmentedMessage.segmentation_index]) \
            .where(and_(SegmentedMessage.segmentation_index.in_(indices_p),
                        SegmentedMessage.day_index == day_index_p)).distinct()
        seg_indices = IRC_CONNECTION.execute(query_).fetchall()

    return seg_indices


def get_senders(day_index_p, seg_index_p):
    """retrieve from DB a list of senders for a given day_index and seg_index"""
    query_ = select([SegmentedMessage.sender_name]) \
        .where(and_(SegmentedMessage.segmentation_index == seg_index_p[0]
                    , SegmentedMessage.day_index == day_index_p))
    senders = IRC_CONNECTION.execute(query_).fetchall()
    return senders


def get_timing_indices(day_index_p, time_index_p, seg_index_p):
    """retrieve from DB a timing_indices for a given day_index, seg_index and time_index.
     timing indices are used for sorting the order of a message in a grouped or
      segmented conversation"""
    query_ = select([SegmentedMessage.row_id]). \
        where(and_(SegmentedMessage.day_index == day_index_p,
                   SegmentedMessage.timing_index == time_index_p,
                   SegmentedMessage.segmentation_index
                   == seg_index_p[0]))
    timing_indices = IRC_CONNECTION.execute(query_).fetchall()
    return timing_indices


def get_db_statistics():
    """retrieve statistical values from DB"""
    query_ = select([func.max(DialogueTurns.turns)])
    max_turn_value = IRC_CONNECTION.execute(query_).first()
    query_ = select([func.min(DialogueTurns.turns)])
    min_turn_value = IRC_CONNECTION.execute(query_).first()
    query_ = select([DialogueTurns.file_name]).where(DialogueTurns.turns
                                                     == max_turn_value[0])
    max_turn_dialogues = IRC_CONNECTION.execute(query_).fetchall()
    query_ = select([DialogueTurns.file_name]).where(DialogueTurns.turns
                                                     == min_turn_value[0])
    min_turn_dialogues = IRC_CONNECTION.execute(query_).fetchall()
    query_ = select([func.sum(DialogueTurns.turns)])
    sum_turn_value = IRC_CONNECTION.execute(query_).first()

    return [min_turn_value[0], max_turn_value[0], min_turn_dialogues,
            max_turn_dialogues, sum_turn_value[0]]
