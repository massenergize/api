# ASYNCHRONOUS TASKS PROCESSING

## Contents
- [Overview](https://pages.github.com/)
- [Overview](https://pages.github.com/)
- [Overview](https://pages.github.com/)



### Taks model

| Field             	| Description                                                                                                                                                                                            	|
|--------------------	|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| name               	| An identifier for the task. it must be unique.                                                                                                                                                         	|
| status             	| The status of the task. Takes the values (`CREATED, RUNNING, SUCCEEDED, FAILED`). Default is CREATED.                                                                                               	|
| job_name           	| The name of the function to trigger when the task is called.The name must be equal to the key of the function in the `FUNCTIONS` dictionary.                                                        	|
| created_at         	| Date and time the task was created.                                                                                                                                                                    	|
| recurring_interval 	| The recurring information. takes the values ( `EVERY_MINUTE,EVERY_MINUTE, EVERY_HOUR, EVERY_DAY, EVERY_MONTH, EVERY_QUARTER, EVERY_YEAR `). the `recurring_details` field should provide specifics 	|
| schedule           	| PeriodicTask model instance provided by celery_beats. The model instance is created from the data provided above                                                                                       	|
| recurring_details  	| A json field to contain the specific time, date, month or months, hour, minutes etc to start the task.                                                                                                 	|
| creator            	| The person who created the task (`UserProfile` - super_admin )                                                                                                                                         	|

<br>

### ADDING FUNCTIONS

- import the function into `jobs.py `  file.
- Added the function as a value to the `FUNCTIONS` dict with a discriptive name.


<br>

### CREATING A TASK BY SUPER ADMIN
URL : DOMAIN + `\api\tasks.create `

payload : 
```js
{
    "name":"task_name",
    "job_name":"send_email",
    "recurring_interval":"EVERY_QUARTER",
    "recurring_details":{
        "months":'2,4,5,8',
        "days":'1',
        "hour":'0'
    }
}

```
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



