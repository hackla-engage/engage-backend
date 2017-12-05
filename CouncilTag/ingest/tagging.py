from abc import ABC
import abc
from CouncilTag.ingest.models import Tag
import random
class TagEngine(ABC):
    '''
    TagEngine is an interface class. You must create a new
    class that takes TagEngine as its base to implement the 
    "find_tags" and "apply_tags" method to use in the meeting injestion process
    '''


    @abc.abstractmethod
    def find_tags(self, agenda_item):

        '''
        This method expects one parameter, an AgendaItem model.
        It should return a list of appropriate tags
        '''
        raise NotImplementedError("find_tags needs to be implemented")

    @abc.abstractmethod
    def apply_tags(self, agenda_item, tags):
        '''
        This method expects two parameters, an AgendaItem model and 
        a list of tags to be applied to the AgendaItem model
        '''
        raise NotImplementedError("apply_tags needs to be implemented")


class RandomTagEngine(TagEngine):
    tags = []
    def __init__(self):
        self.tags = Tag.objects.all()
    
    def find_tags(self, agenda_item):
        n1 = 0
        n2 = 0
        while n1 == n2:
            n1 = random.randrange(0, len(self.tags))
            n2 = random.randrange(0, len(self.tags))
        return [ self.tags[n1], self.tags[n2] ]

    def apply_tags(self, agenda_item, tags):
        for t in tags:
            agenda_item.tags.add(t)
        
        agenda_item.save()
