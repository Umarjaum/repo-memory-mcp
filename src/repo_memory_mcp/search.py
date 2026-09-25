import math, re
from .models import Memory
class SearchEngine:
    def rank(self, memories: list[Memory], query: str, limit: int = 8):
        terms = set(re.findall(r"[\w-]+", query.lower())); phrase=query.lower().strip(); scored=[]
        for m in memories:
            hay=" ".join([m.topic,m.content,m.context_file,m.memory_type,*m.tags]).lower(); score=0.0
            if phrase and phrase in hay: score += 6
            score += sum(1 for t in terms if t in hay) * 1.5
            score += sum(2 for t in terms if t in m.topic.lower())
            score += sum(1 for t in terms if t in m.tags)
            score += {"critical":2.0,"high":1.2,"normal":0.5,"low":0}.get(m.importance,0)
            if score: scored.append((min(score/12,1.0),m))
        return [{"memory_id":m.id,"memory_type":m.memory_type,"relevance_score":round(s,3),"topic":m.topic,"content":m.content,"context":m.context_file,"importance":m.importance} for s,m in sorted(scored,key=lambda x:(x[0],x[1].updated_at),reverse=True)[:limit]]
