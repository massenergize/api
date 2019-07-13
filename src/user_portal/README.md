# User Portal API
This is the official document that defines the GET, POST requests for 
the *user portal api*
> Remember to precede every request with either one of following API host urls
```
API_HOST 
https://api.massenergize.org/
https://api.massenergize.com/
https://apis.massenergize.org/
https://apis.massenergize.com/
```

_for all requests put the args after the url with a **"?"** at the front and an **&** between each arg_ 

_ie ```user/get/page?id={insertPageId}&name={insertPageName}```_

## GET Requests

###### Get Page Information
```
user/get/page
```
This path requests a GET request with one of the following
* id: int
* name: int

###### Get User TODO actions
```
user/get/todo_actions
```
This path requests a GET request with one of the following
* user_id: int
* real_estate_id: int

###### Get User's Completed Actions
```
user/get/completed_actions
```
This path requests a GET request with one of the following
* user_id: int
* real_estate_id: int


###### Get All Events
```
user/get/events/all
user/get/events
```
This path requests a GET request with one of the following
* community_id: int
* is_global: boolean

###### Get One Event
```
user/get/event
```
This path requests a GET request with one of the following
* id: int

###### Get All Actions
```
user/get/community_actions/all
user/get/community_actions
```
This path requests a GET request with one of the following
* community_id: int
* is_global: boolean

###### Get One Action
```
user/get/action
```
This path requests a GET request with one of the following
* id: int

###### Get My Profile
```
user/get/profile
```
This path requests a GET request with one of the following
* email: str
* id: int

###### Get My Households
```
user/get/households/all
user/get/households
```
This path requests a GET request with one of the following
* user_id: int

###### Get One Household
```
user/get/household?id={household_id}
```
This path requests a GET request with one of the following
* id: int

###### Get All Teams
```
user/get/teams/all
```
This path requests a GET request with one of the following
* community_id: int


###### Get One Team
```
user/get/team
```
This path requests a GET request with one of the following
* id: int


###### Get All Communities
```
user/get/communities/all
user/get/communities
```
This path requests a GET request with no args

###### Get One Community
```
user/get/community
```
This path requests a GET request with one of the following
* id: int
* domain: str

###### Get All Graphs
```
user/get/graphs/all
user/get/graphs
```
This path requests a GET request with one of the following
* community_id: int

###### Get One Graph
```
user/get/graph
```
This path requests a GET request with one of the following
* id: int

###### Get testimonials
```
user/get/testimonials
```
This path requests a GET request with one of the following
* community_id
* action_id

## POST Requests
Here are the approved routes to the user portal API


###### Creating New User Accounts
```
user/create/account
user/create/user
```
This path requests a post request with the following information
* full_name: str
* email: str
* firebase_user_info: JSON
* preferred_name: str
* communities: [str] a list of domain names
* default_household: JSON (name, address, community)
* is_service_provider: bool


###### Creating New Goals
```
user/create/goal
```
This path requests a post request with the following information
* name: str
* description: str
* community_id: int
* real_estate_unit: int
* user_id: int
* team_id: int


###### Adding Real Estate Units to Account
```
user/create/real_estate_unit
user/create/household
```
This path requests a post request with the following information
* unit_type: str (options: RESIDENTIAL, COMMERCIAL)
* location: JSON
* community_id: int
* name: str (ie: 'Home','Guest','Vacation'... default: 'property1','property2'...)

###### Creating Teams
```
user/create/team
```
This path requests a post request with the following information
* name: str
* description: str
* community: str


###### Adding Team Members
```
user/add/team_members
```
This path requests a post request with one of the following fields
* user_emails: [str] list of user_emails
* user_ids: [int] list of user_ids


###### Adding Actions to Cart
```
user/add/user_action
```
This path requests a post request with the following information
* action: int
* real_estate_unit: int
* community_id: int
* status: str  (options are TODO, DONE)


###### User Subscribing to MailList
```
user/subscribe
user/add/subscriber

```
This path requests a post request with the following information
* email: str
* community_id: int


###### Adding Testimonial
```
user/add/testimonial
```
This path requests a post request with the following information
* action_id: int
* user_id: int
* community_id: int
* title: str
* body: str
* file: FILE


###### Registering for Events
```
user/register_for_event
```
This path requests a post request with the following information
* user_id: int
* event_id: int
* status: str (options are: INTERESTED, RSVP, SAVE_FOR_LATER)


###### UPDATE UserAction
```
user/update/user_action
```
This path requests a POST request with the following information.
For instance marking an item in the cart from todo to done uses this one
* user_action_id: int
* new_status: str

###### UPDATE Profile
```
user/update/profile
```
This path requests a POST request with the following information
* full_name: str
* email: str

###### UPDATE Event Registration
```
user/update/event_registration
```
This path requests a POST request with the following information.
For instance changing from INTERESTED->RSVP
* id: int
* new_status: str (options are: INTERESTED, RSVP, SAVE_FOR_LATER)


*If we want these to be DELETE requests instead of UPDATE need to change how we store the data by making TeamMember and CommunityMember models*
###### UPDATE Leave Community
```
user/leave/community
```
This path requests a POST request with the following information
* community_id: int
* user_id: int


###### UPDATE Leave Team
```
user/leave/team
```
This path requests a POST request with the following information
* team_id: int
* user_id: int


######

## DELETE Requests

###### DELETE User Account
```
user/delete/user
```
Deletes a UserProfile object
Used to delete a whole account

This path requests a DELETE request with the following information
* id: int

Deleting a UserProfile also deletes:
* All UserActionRelations of that user
* All of the User's households
* All of the User's Goals
* The user's Subscriber object if they have not yet unsubscribed yet
And
* Removes the user from any Team they are in
* Removes the user from any Community they are in

###### DELETE User Action
```
user/delete/user_action
```
Deletes a UserActionRel
Used to remove an Action from both the User's TODO and DONE carts

This path requests a DELETE request with the following information
* id: int


###### DELETE Household
This path requests a DELETE request 
```
user/delete/household?household_id={insertHouseholdID}
user/delete/real_estate_unit?household_id={insertHouseholdID}
```

###### DELETE Team
```
user/delete/team
```
Deletes a Team

This path requests a DELETE request with the following information
* id: int

###### DELETE goal
```
user/delete/goal
```
Deletes a Goal

This path requests a DELETE request with the following information
* id: int

###### DELETE goal
```
user/delete/goal
```
Deletes a Goal

This path requests a DELETE request with the following information
* id: int

###### DELETE Event Registration
```
user/unregister_for_event
```
Removes a user registration for a Event by deleting the EventRegistration object

This path requests a DELETE request with the following information
* event_id: int
* user_id: int

###### DELETE Subscriber
```
user/unsubscribe
user/delete/subscriber
```
Unsubscribes a user

This path requests a DELETE request with the following information
* email: str

