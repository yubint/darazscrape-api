
# Darazscrape Api

This is a REST api made with django Rest Framework that tracks the prices of the products in daraz.com.np. This api uses Django Rest framework for serialization of input and output to transfer through the API endpoint.

It uses Celery-Beat in order to periodically update and track the prices of the products and flag them inactive if they're not tracked by any User. Redis server has been used as a backend for Celery worker.

Django-Rest-Knox has been used for authentication.

## API Reference

#### Login

```http
   POST /api/login
```

| key | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `email` | `string` | **Required**. Email of the User|
| `password` | `string` | **Required**. Password |

#### Register

```http
  POST /api/register
```

| key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `email` | `string` | **Required**. Email of the User|
| `password` | `string` | **Required**. Password |

### Authorization
Authtoken are returned in response during Login or Registration. These need to be send as header in the following format 

| key | value   | 
| :-------- | :------- | 
| `Authorization` | `Token {Auth Token Provided in Response}` | 

So if the Authtoken is `abcd` then the value of `Authorization` should be `Token abcd` 

Endpoints provided below require authorization through authtoken to be accessed.


#### Logout

```http
  POST /api/logout
```

#### Retrieve User 

```http
  GET /api/user 
```

#### Add product

```http
  POST /api/products/create
```

| key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `url` | `string` | **Required**. Url of the Daraz Product to be added|

#### Delete Product

```http
  POST /api/products/delete 
```

| key | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `productId` | `integer` | **Required**. Product Id of the product being deleted|

### Response Format

#### User 

```yaml
{
  id : userId,
  email: userEmail,
  products : [
     {
      id : productId,
      title : productTitle,
      url : productUrl,
      image_url : productImageUrl,
      prices: [
        { date : dateWhenThisPriceWasTracked,
          price : price
        },
        ...
      ]
    },
    ...
  ]
}
 
```

#### Login

```yaml
 {
   expiry : expiryDateofToken,
   token : authToken,
   user : UserObject
 }
```

#### Register

```yaml
  {
    user : UserObject,
    token : authToken
  }
```

#### Create Product

```yaml
  {
     id : productId,
     title : productTitle,
     url : productUrl,
     image_url : productImageUrl,
     prices: [
       { date : dateWhenThisPriceWasTracked,
         price : price
       },
       ...
     ]
  }
```


## Run Locally

Clone the project

```bash
  git clone https://github.com/yubint/darazscrape-api
```

Go to the project directory

```bash
  cd darazscarape-api
```

Install requirements.txt

```bash
  pip install -r requirements.txt
```

Start the Django server

```bash
  python manage.py runserver
```

Start redis server
```bash
  sudo service redis-server start
```

Start celery backend
```bash
  celery -A backend worker -l INFO
```

Start Celery Beat Scheduler
```bash
  celery -A backend beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```


