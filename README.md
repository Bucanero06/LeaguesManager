![V1LeagueManager.png](static%2FV1LeagueManager.png)
Right now this is being tailored to a specific business while remaining modular as to be able to be used for other
projects. The goal is to make this a fully functional league management system that can be used for any sport.

## API Documentation

### Ports

## Needs and Solutions

## Growth Opportunities

## Maintainability and Scalability

* TODO change to page object naming convension
    * PageIdentifier = {A (Admin) or U (User)}{PageName Initials} e.g. ALM (Admin Leagues Management)
    * NameIdentifier = e.g. Commands or new_item
    * TypeIdentifier = {Card, Form, Table, etc.}
  ------------------------------------------------------------------------------------------
    * Preference gives NameIdentifier and TypeIdentifier to the page objects (q.page[{...}]) capitalizing the first
      letter of each word and separated by underscores (snake_case), while the ui object(s)'s NameIdentifier and
      TypeIdentifier are all lowercase and snake_case.
    * On the other hand variables or functions are tend to be lowercase-snake_case (but not strictly, no need to avoid
      capitalization) and classes which are capitalized and follow camelCase convention. This is to make it easier to
      distinguish between the different types of objects. 

# Security

