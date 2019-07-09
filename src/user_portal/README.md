# User Portal API
This is the official document that defines the GET, POST requests for 
the *user portal api*

## GET Requests

###### Get Page Information
```
/user/get/page?page_id={insertPageId}&page_name={insertPageName}
```
This path requests a post request with one of the following
* page_id
* page_name

###### Get All Events
```
/user/get/events/all
/user/get/events
```

###### Get  One Event
```
/user/get/event?id={event_id}
```


###### Get All Actions
```
/user/get/actions/all
/user/get/actions
```

###### Get All Actions
```
/user/get/action?id={action_id}
```

###### Get My Profile
```
/user/get/profile
```

###### Get My Households
```
/user/get/households/all
/user/get/households
```

###### Get One Household
```
/user/get/household?id={household_id}
```

###### Get All Teams
```
/user/get/teams/all?community_id={community_id}
```


###### Get One Team
```
/user/get/team?id={team_id}
```


###### Get All Communities
```
/user/get/communities/all
/user/get/communities
```

###### Get One Community
```
/user/get/community?domain={community_domain}
```

###### Get All Graphs
```
/user/get/graphs/all
/user/get/graphs
```

###### Get One Graph
```
/user/get/graph?id={graph_id}
```



## POST Requests
Here are the approved routes to the user portal API


###### Creating New User Accounts
```
/user/create/account
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
/user/create/goal
```
This path requests a post request with the following information
* name: str
* description: str
* community_domain: str
* real_estate_unit: int
* team: int


###### Adding Real Estate Units to Account
```
/user/create/real_estate_unit
/user/create/household
```
This path requests a post request with the following information
* unit_type: str (options: RESIDENTIAL, COMMERCIAL)
* location: JSON
* community_domain: str

###### Creating Teams
```
/user/create/team
```
This path requests a post request with the following information
* name: str
* description: str
* community: str


###### Adding Team Members
```
/user/subscribe
```
This path requests a post request with one of the following fieldss
* email: str
* emails: list of emails as strings


###### Adding Actions to Cart
```
/user/add/action
```
This path requests a post request with the following information
* action: int
* real_estate_unit: int
* community_domain: str
* status: str  (options are TODO, DONE, SAVE_FOR_LATER)


###### User Subscribing to MailList
```
/user/subscribe
```
This path requests a post request with the following information
* email: str
* full_name: str


###### Adding Testimonial
```
/user/add/testimonial
```
This path requests a post request with the following information
* action: id
* title: str
* body: str
* file: FILE


###### Registering for Events
```
/user/add/event
```
This path requests a post request with the following information
* event: int
* community_domain: str
* status: str (options are: INTERESTED, RSVP, SAVE_FOR_LATER)


