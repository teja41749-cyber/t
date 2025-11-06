import requests
import json
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted

class ActionValidateRelationship(Action):
    def name(self) -> Text:
        return "action_validate_relationship"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get relationship details from tracker
        relationship_type = tracker.get_slot("relationship_type")
        source_class = tracker.get_slot("source_class")
        target_class = tracker.get_slot("target_class")

        if relationship_type and source_class and target_class:
            # Generate appropriate response based on relationship type
            response = f"Got it! I'll update the relationship between {source_class} and {target_class} to {relationship_type}."

            # Ask for multiplicity if needed
            if relationship_type in ["composition", "association", "aggregation"]:
                response += " What should be the multiplicity (1:1, 1:many, many:many, etc.)?"

            dispatcher.utter_message(text=response)

            return [SlotSet("target_relationship", f"{source_class}-{target_class}")]

        return []

class ActionModifyDiagram(Action):
    def name(self) -> Text:
        return "action_modify_diagram"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get modification details
        modification_type = tracker.get_slot("modification_type")
        target_class = tracker.get_slot("target_class")
        target_relationship = tracker.get_slot("target_relationship")

        # In a real implementation, this would call the backend API
        # For now, we'll just acknowledge the change
        if modification_type == "class" and target_class:
            action = f"modified the {target_class} class"
        elif modification_type == "relationship" and target_relationship:
            action = f"updated the {target_relationship} relationship"
        else:
            action = "updated your diagram"

        dispatcher.utter_message(text=f"Perfect! I've {action}. The diagram has been updated with your changes.")

        return [SlotSet("target_class", None), SlotSet("target_relationship", None)]

class ActionAddClass(Action):
    def name(self) -> Text:
        return "action_add_class"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get class name from the latest message
        latest_message = tracker.latest_message.get('text', '')

        # Extract class name (simplified extraction)
        class_name = latest_message.replace('add ', '').replace('class', '').strip()

        if class_name:
            # Call backend API to add class
            try:
                api_response = self._call_backend_api('add_class', {'class_name': class_name})
                dispatcher.utter_message(text=f"Great! I've added the {class_name} class to your diagram.")
                return [SlotSet("target_class", class_name)]
            except Exception as e:
                dispatcher.utter_message(text=f"Sorry, I couldn't add the class. Please try again.")
        else:
            dispatcher.utter_message(text="I didn't catch the class name. What would you like to name the new class?")

        return []

class ActionRemoveClass(Action):
    def name(self) -> Text:
        return "action_remove_class"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        class_name = tracker.get_slot("class_name")

        if class_name:
            dispatcher.utter_message(text=f"I've removed the {class_name} class from your diagram.")
            return [SlotSet("class_name", None)]
        else:
            dispatcher.utter_message(text="Which class would you like me to remove?")

        return []

class ActionAddAttribute(Action):
    def name(self) -> Text:
        return "action_add_attribute"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        class_name = tracker.get_slot("class_name")
        attribute_name = tracker.get_slot("attribute_name")
        data_type = tracker.get_slot("data_type")

        if class_name and attribute_name:
            data_type = data_type or "String"
            dispatcher.utter_message(text=f"Added {attribute_name}: {data_type} to the {class_name} class.")
            return [SlotSet("attribute_name", None), SlotSet("data_type", None)]
        else:
            dispatcher.utter_message(text="What attribute would you like to add?")

        return []

class ActionAddMethod(Action):
    def name(self) -> Text:
        return "action_add_method"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        class_name = tracker.get_slot("class_name")
        method_name = tracker.get_slot("method_name")

        if class_name and method_name:
            dispatcher.utter_message(text=f"Added {method_name}() method to the {class_name} class.")
            return [SlotSet("method_name", None)]
        else:
            dispatcher.utter_message(text="What method would you like to add?")

        return []

class ActionExportDiagram(Action):
    def name(self) -> Text:
        return "action_export_diagram"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        export_format = tracker.get_slot("export_format")

        if export_format:
            dispatcher.utter_message(text=f"Your diagram has been exported in {export_format} format. You should see a download prompt.")
            return [SlotSet("export_format", None)]
        else:
            dispatcher.utter_message(text="What format would you like to export your diagram in?")

        return []

class ActionShowContext(Action):
    def name(self) -> Text:
        return "action_show_context"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Get current diagram context from tracker or backend
        # For now, provide a generic response
        class_count = tracker.get_slot("class_count") or "several"
        relationship_count = tracker.get_slot("relationship_count") or "some"

        context_message = f"Your current diagram has {class_count} classes and {relationship_count} relationships. "
        context_message += "I can help you add more classes, modify relationships, or export the diagram when you're ready."

        dispatcher.utter_message(text=context_message)
        return []

class ActionProvideHelp(Action):
    def name(self) -> Text:
        return "action_provide_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        help_message = """I can help you with several tasks to refine your UML diagram:

🏗️ **Structure Changes:**
- Add new classes to your diagram
- Remove classes you don't need
- Modify existing classes

🔗 **Relationship Management:**
- Change relationship types (composition, association, inheritance, aggregation)
- Set relationship multiplicities (1:1, 1:many, etc.)
- Remove unwanted relationships

📝 **Class Details:**
- Add attributes with specific data types
- Add methods with parameters
- Remove unnecessary attributes or methods

💾 **Export Options:**
- Export as Mermaid code
- Export as JSON format
- Save your diagram for later use

Just tell me what you'd like to do, or ask me to explain any part of your current diagram!"""

        dispatcher.utter_message(text=help_message)
        return []

    def _call_backend_api(self, action: str, data: Dict) -> Dict:
        """Helper method to call backend API for diagram modifications."""
        # This would be implemented to call the actual Flask backend
        # For now, return a mock response
        return {"status": "success", "message": f"Action {action} completed"}