#coding=utf-8
import sys
from wit import Wit
import uuid
import json
import requests

global session_id
session_id = None

API_HOST = 'http://www.anyong.biz:9427/pepper/'

def req(meth,path):
    url = API_HOST + path
    print url
    res = requests.request(meth,url)
    json = res.json()
    return json
    
class WitConversation:
    _intent_state = {"say_hello":0,"watch_album":1,"person":2,"listen_music":3,"confuse":4}
    _state = None
    _personList = ['寶弟','暄暄']
    _responseMsg = ""
    _musicName = "外婆的澎湖灣"

    def __init__(self):
        self.access_token='3Y2PWQBZDNOXGIRR46CNAOYBQJ5GYN3C'
        self.actions = {
        'send': self.__send,
        'sayHello': self.__sayHello,
        'getPerson': self.__getPerson,
        'checkMusic': self.__checkMusic,
        }
        self.client = Wit(access_token=self.access_token, actions=self.actions)

    def __first_entity_value(self,entities, entity):
        if entity not in entities:
            return None
        val = entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def __send(self,request, response):
        self._responseMsg = str(response['text'])
        print self._responseMsg

    def __sayHello(self,request):
        context = request['context']
        entities = request['entities']
        # print entities
        greet = self.__first_entity_value(entities,'greeting')
        # print greet
        context['greet'] = greet
        return context

    def __getPerson(self,request):
        context = request['context']
        entities = request['entities']
        # print entities
        person_list=self._personList
        if 'misunderstand' in context:
            del context['misunderstand']
        try:
            person = self.__first_entity_value(entities,'name')
            # print type(person),person
            if person.encode('utf8') in person_list:
                context['correct'] = person
            else:
                context['misunderstand'] = person
        except Exception, e:
            pass
        return context

    def __checkMusic(self,request):
        context = request['context']
        entities = request['entities']
        correct_music_name = self._musicName
        try:
            get_music_name = self.__first_entity_value(entities,'music_name').encode('utf-8')
            if get_music_name == correct_music_name:
                context['correct'] = get_music_name
            else:
                context['wrong'] = correct_music_name
        except:
            context['wrong'] = correct_music_name
        return context

    def sendMsg(self,text):
        global session_id
        if session_id is None:
            session_id = uuid.uuid1()
        context = self.client.run_actions(session_id, text)

    def updatePersonList(self,new_list):
        self._personList = new_list

    def getResponseMsg(self):
        return self._responseMsg

    def getResponseState(self):
        return self._intent_state[self._state]

    def getPhotoQuestion(self):
        url = 'photo/question'
        resp = req('GET',url)
        self._personList.append(resp['data'][0]['name'].encode('utf-8'))
        img_url = resp['data'][0]['img'].encode('utf-8')
        return img_url

    def getSongQuestion(self):
        url = 'song/question'
        resp = req('GET',url)
        self._musicName =  resp['data'][0][''].encode('utf-8')
        return name

    def postSound(self,input):
        url = 'https://api.wit.ai/speech?v=20160526'
        file = input
        sound = open(file, "rb").read()
        resp = requests.request('POST',url,
            headers={
            'authorization': 'Bearer ' + self.access_token,
            'content-Type': 'audio/wav'},
            data=sound)
        jresp = resp.json()
        if 'intent' in jresp['entities']:
            msg = json.dumps(jresp['_text'], ensure_ascii=False).encode('utf-8')
            self._state = self.__first_entity_value(jresp['entities'],'intent')
            self.sendMsg(msg)
            return self.getResponseMsg()
        else:
            self._state = "confuse"
            return '我聽不太懂，你可以再說一遍嗎？我還在學習中'

    def postVideo(self):
        url = 'http://192.168.31.211:3030/upload'
        files = {'file': open('recording_video.avi', 'rb')}
        r = requests.post(url, files=files)
        print r 

if __name__ == '__main__':
    c = WitConversation()
    c.sendMsg('早安');
    c.sendMsg('聽歌');
    c.sendMsg('外婆的澎湖灣吧');
    c.sendMsg('我忘記了');
    c.sendMsg('好啊 好懷念喔');
    c.sendMsg('是寶弟吧');
    c.sendMsg('不知道');   
