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

## GET Requests

###### Get Page Information
```
user/get/page?page_id={insertPageId}&page_name={insertPageName}
```
This path requests a GET request with one of the following
* page_id
* page_name

###### Get User TODO actions
```
user/get/todo_actions
```

###### Get User's Completed Actions
```
user/get/completed_actions
```


###### Get All Events
```
user/get/events/all?community_domain={community_domain}
user/get/events?community_domain={community_domain}
```

###### Get One Event
```
user/get/event?id={event_id}
```


###### Get All Actions
```
user/get/community_actions/all?community_domain={community_domain}
user/get/community_actions?community_domain={community_domain}
```

###### Get One Action
```
user/get/action?id={action_id}
```

###### Get My Profile
```
user/get/profile
```

###### Get My Households
```
user/get/households/all
user/get/households
```

###### Get One Household
```
user/get/household?id={household_id}
```

###### Get All Teams
```
user/get/teams/all?community_id={community_id}
```


###### Get One Team
```
user/get/team?id={team_id}
```


###### Get All Communities
```
user/get/communities/all
user/get/communities
```

###### Get One Community
```
user/get/community?domain={community_domain}
```

###### Get All Graphs
```
user/get/graphs/all?community_domain={community_domain}
user/get/graphs?community_domain={community_domain}
```

###### Get One Graph
```
user/get/graph?id={graph_id}
```



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
* community_domain: str
* real_estate_unit: int
* team: int


###### Adding Real Estate Units to Account
```
user/create/real_estate_unit
user/create/household
```
This path requests a post request with the following information
* unit_type: str (options: RESIDENTIAL, COMMERCIAL)
* location: JSON
* community_domain: str

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
* emails: [str] list of emails as strings


###### Adding Actions to Cart
```
user/add/user_action
```
This path requests a post request with the following information
* action: int
* real_estate_unit: int
* community_domain: str
* status: str  (options are TODO, DONE)


###### User Subscribing to MailList
```
user/subscribe
user/add/subscriber

```
This path requests a post request with the following information
* email: str
* full_name: str


###### Adding Testimonial
```
user/add/testimonial
```
This path requests a post request with the following information
* action: id
* title: str
* body: str
* file: FILE


###### Registering for Events
```
user/register_for_event
```
This path requests a post request with the following information
* event: int
* community_domain: str
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

## DELETE Requests

###### DELETE User Action
This path requests a DELETE request 
```
user/delete/user_action/{user_action_id}
```


###### DELETE User Account
This path requests a DELETE request
```
user/delete/user/{user_action_id}
```
