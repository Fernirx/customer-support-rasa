from typing import Any, Text, Dict, List
from rasa.engine.graph import GraphComponent, ExecutionContext
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.message import Message
from rasa.engine.recipes.default_recipe import DefaultV1Recipe

@DefaultV1Recipe.register(
    is_trainable=False,
    component_types=["MessagePreprocessor"]
)
class RemoveDuplicateTokens(GraphComponent):
    """Xử lý message.tokens trước khi vào DIETClassifier."""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "RemoveDuplicateTokens":
        return cls()

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            tokens = message.get("tokens", [])
            new = []
            prev = None
            for t in tokens:
                if t.text != prev:
                    new.append(t)
                prev = t.text
            message.set("tokens", new, add_to_output=True)
        return messages
