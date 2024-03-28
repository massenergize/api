# Created by Tahiru at 25/03/2024
## Feature Architecture: Community Notifications Management 
 
### 1. Introduction
The Community Notifications Management feature provides administrators with the ability to manage  notifications sent to the community. Administrators have the ability to create, update, and view these notification settings. This feature also allows administrators to pause or resume the sending of notifications to the community. For more details, please refer to this [GitHub Issue](https://github.com/massenergize/frontend-admin/issues/1075).

### 2. Feature Overview

The Community Notifications Management feature is designed to provide a robust and flexible system for managing community notifications. It allows administrators to create, update, and manage notification settings for their community. 

The feature is built around the `CommunityNotificationSetting` model, which stores the configuration for each type of notification that can be sent to the community. Administrators can specify the type of notification, whether or not it's active, and optionally, a date to activate it.

The feature provides several endpoints for managing these settings, including endpoints for creating, updating, and fetching notification settings. 

The business logic for the feature ensures that notifications are sent out according to the settings specified by the administrators. For example, a notification setting can be scheduled to activate at a future date, or it can be set to active immediately. 

This feature is crucial for keeping the communities informed about important updates and events. It provides a way for administrators to communicate effectively with their communities, ensuring that everyone stays connected and informed.


### 3. Detailed Design

#### 3.1 Data Models

The `CommunityNotificationSetting` model is the primary data model for this feature. It includes the following fields:

- `id`: A unique identifier for each notification setting. [PK]
- `community`: A foreign key to the `Community` model, representing the community for which the notification setting is applicable. [FK]
- `updated_by`: A foreign key to the `UserProfile` model, representing the user who last updated the notification setting. [PK]
- `notification_type`: A string field representing the type of notification. The choices for this field are defined in `COMMUNITY_NOTIFICATION_TYPES`, which are the feature flag keys of the notifications. This field is used to get the feature flag associated with the notification setting.
- `is_active`: A boolean field indicating whether the notification setting is active.
- `activate_on`: A date field specifying when the notification setting should be activated.
- `created_at`: A datetime field indicating when the notification setting was created.
- `updated_at`: A datetime field indicating when the notification setting was last updated.
- `more_info`: A JSON field for storing additional information about the notification setting.

#### 3.2 Endpoints

The main endpoints for this feature include:

- `POST /communities.notifications.settings.list`: Accepts `{community_id:int}` || Returns a dictionary of all notification settings for a given community. The key is the notification type and the value is the notification setting.
- `POST /communities.notifications.settings.set`: Accepts `{id:str, is_active:bool, activate_on:date or None}` ||  Updates a specific notification setting for a given community. Returns the updated notification setting.

Note: The creation is initiated using the list endpoint when the community is permitted to access the feature(i.e. feature flag) but hasn't configured any notification settings yet. The set endpoint is used to update the notification settings.

#### 3.3 Business Logic

The primary business logic for this feature is as follows:

- When a new notification setting is created, the `is_active` field is set to `True` by default.
- The `activate_on` field can be used to schedule when the notification setting should be activated. If this field is not set and is `is_active` is true, the notification setting is activated immediately.
- When a notification setting is updated, the `updated_by` field is set to the user who made the update.
-


### 4. Deployment 

Activating the Community Notifications Management feature involves a series of steps to affirm the new functionality's seamless incorporation into the current system and the expected operation in a live setting.

#### 4.1 Database Migration

For this feature to function correctly, it mandates the introduction of new or amended database models, specifically `CommunityNotificationSetting`. This dictates the necessity of a database migration. Such a migration ensures updating the database schema to accommodate the modifications implicated by this feature.

#### 4.2 Functionality Testing

Post-deployment, it's essential to perform a thorough evaluation of the feature within the live environment. This process entails a combination of automated and manual testing mechanisms to assert the feature's performance and intended functionality.

### 5. Conclusion

The Community Notifications Management feature serves as a sturdy and scalable system for overseeing community notifications. It presents administrators with the necessary toolset to maintain sound communication with the community, notifying them of crucial updates and events.

The specification and realization of this feature have been meticulously executed to ensure user-friendly interaction and reliability. Its performance has been subjected to rigorous testing to warrant its operation under various circumstances.

Equipped with this feature, administrators can oversee community notifications with certainty, backed by a reliable and efficient system.