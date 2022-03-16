# ASYNCHRONOUS TASKS PROCESSING


### HOW IT WORKS

...............................................





### Taks model

| Field             	| Description                                                                                                                                                                                            	|
|--------------------	|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| name               	| An identifier for the task. it must be unique.                                                                                                                                                         	|
| status             	| The status of the task. Takes the values (`CREATED, RUNNING, SUCCEEDED, FAILED`). Default is CREATED.                                                                                               	|
| job_name           	| The name of the function to trigger when the task is called.The name must be equal to the key of the function in the `FUNCTIONS` dictionary.                                                        	|
| created_at         	| Date and time the task was created.                                                                                                                                                                    	|
| recurring_interval 	| The recurring information. takes the values ( `EVERY_MINUTE,EVERY_MINUTE, EVERY_HOUR, EVERY_DAY,EVERY_WEEK,  EVERY_MONTH, EVERY_QUARTER, EVERY_YEAR `). the `recurring_details` field should provide specifics 	|
| schedule           	| PeriodicTask model instance provided by celery_beats. The model instance is created from the data provided above                                                                                       	|
| recurring_details  	| A json field to contain the specific time, date, month or months, hour, minutes etc to start the task.                                                                                                 	|
| creator            	| The person who created the task (`UserProfile` - super_admin )                                                                                                                                         	|

<br>

### ADDING FUNCTIONS

- import the function into `jobs.py `  file.
- Added the function as a value to the `FUNCTIONS` dict with a discriptive name.

_NOTE:_ The code does not support direct addition of arguments


<br>

###  CRUD  OPERATIONS

#### 1. CREATE
URL : DOMAIN + `\api\tasks.create `

payload : 
```js
{
    "name":"Policy Change Email To Users",
    "job_name":"send_email",
    "recurring_interval":"ONE_OFF",
    "recurring_details":{
        "day_of_month":'2,4,5,8',
        "day_of_week":'1',
        "month_of_year":'*',
        "minute":'*',
        "hour":'*',
        
    }
}

```
_NOTE:_ 

- `recurring_details` must be `json stringified.`
- For `recurring_details` fields that you don't wish to populate, use `*` as the value.


response: 
```js
{
    "data": {
        ...created_data
    },
    "error": null,
    "success": true
}
 ```


#### 2. GET TASK INFO
URL : DOMAIN + `\api\tasks.info `

payload : 
```js
{
    "id":1,
}

```

response: 
```js
{
    "data": {
        ...task data
    },
    "error": null,
    "success": true
}
 ```
#### 3. DELETE TASK
URL : DOMAIN + `\api\tasks.delete `

payload : 
```js
{
    "id":1,
}

```

response: 
```js
{
    "data": {
        ...task data
    },
    "error": null,
    "success": true
}
 ```

#### 4. UPDATE TASK INFO
URL : DOMAIN + `\api\tasks.update `

payload : 
```js
{
    "id":1,
    "job_name":"send_email",
    "recurring_interval":"EVERY_QUARTER",
    "recurring_details":{
        "month_of_year":'2,4,5,8',
        "day_of_week":'*',
        "day_of_month":'1',
        "minute":'*',
        "hour":'*',
        
    }
}

```

response: 
```js
{
    "data": {  
    "id":1,
    "name":"Policy Change Email To Users",
    "job_name":"send_email",
    "recurring_interval":"EVERY_QUARTER",
    "recurring_details":{
        "month_of_year":'2,4,5,8',
        "day_of_week":'*',
        "day_of_month":'1',
        "minute":'*',
        "hour":'*',
        
    } },
    "error": null,
    "success": true
}
 ```






