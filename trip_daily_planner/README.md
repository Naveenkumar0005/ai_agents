# Trip Daily Planner with Traveler's Information Input and Email Sending Tool

### It has following features:

* The application will get traveler's necessary information: destination, flight, hotel location, trip duration, personal interests, dining restrictions and preferences and email from Gradio UI. The application will plan daily activities and restaurants for the trip and send daily planner to the email provided.  For example, if I have personal interests as
  `Enjoy historic and cultural sites. An out-of-town day trip is fine. Include biking activities in one of days`
  It will plan a bike ride and out-of-town day trip for me. It will honor dining retrictions or preferences too.
  
* The crew has 4 agents: personalized_activity_planner, restaurant_scout, itinerary_compiler and email_agent and 4 tasks:
  personalized_activity_planning_task, restaurant_location_scout_task, itinerary_compilation_task and format_send_email_task
  'itinerary_compiler' will gather info from 'personalized_activity_planner' and 'restaurant_scout' and compile into strictured pydantic output of Itinerary and email agent will reformat into HTML, subject line and send  email accordingly.

