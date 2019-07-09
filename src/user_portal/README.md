# User Portal API

### POST Requests

###### Creating New User Accounts
```
/user/create/account
```
This path requests a post request with the following information
* full_name: str
* email: str
* firebase_user_info: JSON
* preferred_name: : str
* community: int

###### Creating New Goals
```
/user/create/goal
```
This path requests a post request with the following information
* name: str
* description: str
* community: int
* real_estate_unit: int
* team: int


###### Adding Real Estate Units to Account
```
/user/create/real_estate_unit
```
This path requests a post request with the following information
* unit_type: str (options: RESIDENTIAL, COMMERCIAL)
* location: JSON
* community: int

###### Creating Teams
```
/user/create/real_estate_unit
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
* community: int
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
* community: int
* status: str (options are: INTERESTED, RSVP, SAVE_FOR_LATER)


