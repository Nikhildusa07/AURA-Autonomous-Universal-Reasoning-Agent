from backend.app.memory.memory import memory


class LearningEngine:

    def learn(self, key: str, value):
        memory.remember_fact(key, value)

        return {
            "success": True,
            "key": key,
            "value": value
        }

    def recall(self, key: str):
        return memory.get_fact(key)

    def get_all_knowledge(self):
        return memory.get_all_facts()


learning_engine = LearningEngine()