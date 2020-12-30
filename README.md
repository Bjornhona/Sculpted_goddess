## Sculpted Goddess
 Sculpting Goddess is a web applilcation and a tool that helps women sculpt and take care of their bodies in a healthy way. It keeps track on personal data and calculates your macro daily needs as well as gives the opportunity to search and save favorite recipes in a large selection of healthy recipes. All recipes give nutritional information to help to plan what you eat daily in accordance to dietary needs.

## Motivation
I was inspired to build this web application for the purpose of having a convenient tool to help me and other women sculpt and take care of their bodies in a healthy way. It helps me set up my personal meal plans so that I easier can achieve my fitness goals. It is also my Final Project as part of the Harvard course CS50x on edX, Introduction to Computer Science.
 
## Screenshots
Design in Adobe XD
[![Home Sculpted Goddess](https://github.com/Bjornhona/Sculpted_goddess/blob/master/static/images/screen_shot.png)](https://github.com/Bjornhona/Sculpted_goddess/blob/master/static/images/screen_shot.png)
[![Home Sculpted Goddess](https://github.com/Bjornhona/Sculpted_goddess/blob/master/static/images/screen_shot_2.png)](https://github.com/Bjornhona/Sculpted_goddess/blob/master/static/images/screen_shot_2.png)

## Tech/framework used
Server-side rendering
<b>Built with</b>
- Python
- Flask
- Javascipt
- HTML
- SCSS
- Flexbox
- SQL

<b>Other tools used<b>
- Visual Studio Code
- Design in Adobe XD
- Trello Board

## Features
The project offers a huge database of Recipes with their individual nutrition data. The user is able to search for recipes and store their favourite ones for later. A macronutrient calculator is implemented that asks the user for personal data and goals and then suggests the macronutrient ratio and BMI, Body Mass Index, so that it will be easier to adapt the perfect meal plan. The project also contains a Contact Form where interested clients can email their contact data and send a message. The web application is open to enter and read for anyone, but it is necessary to sign up and be logged in to use it's main features.

## Code Example
```
  # Search hits from API that matches a search-word the user entered in the Search input field
  search_word = request.form.get("search_word")
  hits = []
  count = 0
  response = None

  try:
      response = requests.get("https://api.edamam.com/search?q=" + search_word + "&app_id=a8f562ca&app_key=9e763f1edd4c3c739eb2506f1dbfrgf5&from=0&to=12&calories=591-722")
  except HTTPError as http_err:
      print(f"HTTP error occurred: {http_err}")
  except Exception as err:
      print(f"An error ocurred: {err}")

  if response.status_code == 200:
      responseJSON = response.json()
      hits = responseJSON["hits"]
      count = responseJSON["count"]

  # Check what recipes this user have saved in DB recipes table
  savedResp = engine.execute("SELECT * FROM recipes WHERE user_id=:user_id", user_id=session['user_id']);
  saved = savedResp.fetchall()

  for row in saved:
      savedId = row[0]

      for hit in hits:
          hitId = hit['recipe']['uri']

          # Adds key value pair in hits
          if hitId == savedId:
              hit['saved'] = True

```

## API Reference
Edamam recipe search API
https://developer.edamam.com/edamam-docs-recipe-api

## Credits
Thank you very much to David J. Malan for great explanations during all of his teaching sessions and also to the rest of the team at Harvard CS50 for a very professional build up couse.
I found good inspiration for this particular project online, great thanks to https://dribbble.com/shots/7087226-Meal-Planning-Web-App-Design/attachments/88969?mode=media by Kyle Torres.