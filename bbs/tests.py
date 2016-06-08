# encoding:utf-8
from __future__ import unicode_literals

from django.test import TestCase
# Create your tests here.
from bbs.models import NewThread


class ThreadTestCase(TestCase):
    # def setUp(self):
    #     NewThread('高清电影', '哈利波特与阿兹卡班的囚徒',
    #               '''哈利（丹尼尔雷德克里夫）即将在霍格沃兹渡过第三个年头，此时在阿兹塔班却传出恶棍小天狼星（加里奥德曼）越 狱的消息。据说小天狼星正是背叛哈利父母的好友，他的教父，而这次小天狼星越狱似乎正是为了找他。哈利的心里悄悄的滋生了为父母报仇的想法，期待着小天狼星的出现''',
    #               types=['神话'], area=['美国'])

    def test_thread(self):
        NewThread('高清电影', '哈利波特与阿兹卡班的囚徒',
                  '''哈利（丹尼尔雷德克里夫）即将在霍格沃兹渡过第三个年头，此时在阿兹塔班却传出恶棍小天狼星（加里奥德曼）越 狱的消息。据说小天狼星正是背叛哈利父母的好友，他的教父，而这次小天狼星越狱似乎正是为了找他。哈利的心里悄悄的滋生了为父母报仇的想法，期待着小天狼星的出现''',
                  types=['神话'], area=['美国'])
