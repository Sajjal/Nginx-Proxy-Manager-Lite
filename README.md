[![GitHub stars](https://img.shields.io/github/stars/Sajjal/Nginx-Proxy-Manager-Lite)](https://github.com/Sajjal/Nginx-Proxy-Manager-Lite/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Sajjal/Nginx-Proxy-Manager-Lite)](https://github.com/Sajjal/Nginx-Proxy-Manager-Lite/issues)
<a href="https://hub.docker.com/repository/docker/mrsajjal/npmlite">
<img src="https://img.shields.io/docker/pulls/mrsajjal/npmlite.svg">
</a>
![GitHub language count](https://img.shields.io/github/languages/count/Sajjal/Nginx-Proxy-Manager-Lite)
![GitHub repo size](https://img.shields.io/github/repo-size/Sajjal/Nginx-Proxy-Manager-Lite)

# Welcome

## Thank you for exploring S & D Nginx Proxy Manager Lite.

It is a lightweight Docker container for managing Nginx hosts with REST api and a simple, minimal web UI.
This application is developed using Flask in the backend, and VueJS with Quasar in the frontend. SQLite is used as a database.

## Background (_Why this application was developed?_)

I have used [Nginx Proxy Manager](https://github.com/jc21/nginx-proxy-manager) to manage proxy hosts in past and I really loved it. This time, I am working on a project where users require an option to frequently update host configuration programmatically; i.e. similar to **Nginx Proxy Manager**. Therefore, I created a REST API for that purpose. After using the api for few days, I decided to pack it as a docker container for easy deployment. While doing so, I thought why not create a simple user interface and give user an option to either enable/disable both Web UI and REST API. Hence, here it is.

It is the lite version of original **Nginx Proxy Manager** and only contains basic features. I recommend to use [Nginx Proxy Manager](https://github.com/jc21/nginx-proxy-manager) should you require additional features.

---

## Prerequisites:

### Docker:

- Install **Docker** in your machine

### Ports:

- Make sure port `80` and `443` are open and available in your machine

---

## Quick Start:

1. Create a new `docker network`:

   ```
   docker network create npmlite_sd
   ```

2. Pull and run `npmlite docker container`:

   ```
   docker run -p 80:80 -p 443:443 --network npmlite_sd -v ~/npmlite/data:/data -v ~/npmlite/ssl:/etc/letsencrypt --name npmlite -d  mrsajjal/npmlite
   ```

3. Go to `http://localhost` or `http://your-machine-ip` **Enjoy.**

---

## Configuration

- You can choose to either enable or disable `Web Interface` and `Rest API`
- If you followed above `docker run command`, edit: `~/npmlite/data/npmlite_config/config.json`
- If you mapped different directory, find and edit `/data/npmlite_config/config.json`

  | Configuration option | Type     | Description                                                                    |
  | :------------------- | :------- | :----------------------------------------------------------------------------- |
  | `enable_web_portal`  | `bool`   | Enable or disable web portal. Default is `true`                                |
  | `jwt_secret_key`     | `string` | Secret to protect **JWT token** with. **Required** if web interface is enabled |
  | `JWT_COOKIE_SECURE`  | `bool`   | Enable or disable **HTTPS only JWT cookies**. Default is `false`               |
  | `enable_rest_api`    | `bool`   | Enable or disable **REST API**. Default is `false`                             |
  | `api_key`            | `string` | API Key for REST API endpoints. **Required** if REST API is enabled            |

> **Info**: It is recommended to change `jwt_secret_key` and **restart** the container after making configuration changes.

---

## REST API

If you have enabled `REST API`, you can consume it and programmatically manage nginx hosts.

### Check API Status:

- Check if the API server is running
- **Endpoint:** `GET /api/status`

  ```
  curl http://your_machine_ip/api/status
  ```

- Returns:

  ```JSON
  {"serverStatus":"API Server Up & Running..."}
  ```

### List Hosts:

- List all availabel Hosts
- **Endpoint:** `GET /api/list`

  ```
  curl http://your-machine-ip/api/list -H "Authorization: Bearer <api_key>"
  ```

- Returns:

  ```JSON
  {
  "domain_list": [
     {
        "HSTS": "True",
        "block_exploit": "True",
        "domain": "example.com",
        "enableSSL": "True",
        "forceSSL": "True",
        "http2": "True",
        "id": "b3dc6c8667bc46c4b885f88fe723b40e",
        "ips": [
        {
           "ip": "localhost",
           "port": "40045"
        }
        ],
        "is_disabled": 0,
        "redirect_url": "",
        "static_path": "",
        "timestamp": "1635753241116",
        "type": "reverse_proxy",
        "userID": "e1a915e55ddc4f14b52dc4632ed51e09",
        "websocket": "True"
     }
  ]
  }
  ```

### Request SSL from Let's Encrypt:

- **Endpoint:** `POST /api/requestSSL`

  | Parameter      | Type     | Description                                                        |
  | :------------- | :------- | :----------------------------------------------------------------- |
  | `domain`       | `string` | **Required**. Domain you want to request SSL certificate for       |
  | `email`        | `string` | **Required**. Email address to setup an account with Let's Encrypt |
  | `agree_le_tos` | `bool`   | **Required**. Accept or deny Let's Encrypt's terms of services     |

  ```
  curl -X POST http://your-machine-ip/api/requestSSL
    -H 'Content-Type: application/json'
    -H 'Authorization: Bearer <api_key>'
    -d '{"domain":"example.com", "email":"me@mydomain.com", "agree_le_tos":true}'
  ```

- Returns:

  ```JSON
  {
  "userID": "e1a915e55ddc4f14b52dc4632ed51e09",
  "domain": "example.com",
  "ssl_cert_path": "/etc/letsencrypt/live/example.com/fullchain.pem",
  "ssl_key_path": "/etc/letsencrypt/live/example.com/privkey.pem"
  }
  ```

### List SSL Certificates:

- List all available SSL certificates
- **Endpoint:** `GET /api/listSSL`

  ```
  curl http://your-machine-ip/api/listSSL -H "Authorization: Bearer <api_key>"
  ```

- Returns:

  ```JSON
  {
  "ssl_list": [
     {
        "cert_info": {
        "ssl_active_from": "Nov 1 2021",
        "ssl_expiry": "Jan 30 2022",
        "ssl_issuer": "Let's Encrypt"
        },
        "domain": "example.com",
        "id": "51976cbc949a450ab9bcc1892242b0e0",
        "ssl_cert_path": "/etc/letsencrypt/live/example.com/fullchain.pem",
        "ssl_key_path": "/etc/letsencrypt/live/example.com/privkey.pem",
        "timestamp": "1635753215599",
        "userID": "e1a915e55ddc4f14b52dc4632ed51e09"
     }
  ]
  }
  ```

### Add New Host

- **Endpoint:** `POST /api/create`

  | Parameter       | Type                    | Description                                                                       |
  | :-------------- | :---------------------- | :-------------------------------------------------------------------------------- |
  | `domain`        | `string`                | **Required**. Domain name that you want to add                                    |
  | `type`          | `string`                | **Required**. `static`, `redirect` or `reverse_proxy`                             |
  | `static_path`   | `string`                | Location of static files. **Required** if `type` is `static`                      |
  | `redirect_url`  | `string`                | URL to redirect. **Required** if `type` is `redirect`                             |
  | `ips`           | `array/list of objects` | IP/Hostname and/or port to forward. **Required** if `type` is `reverse_proxy`     |
  |                 |                         | **EXample**: `[ { "ip": "localhost", "port": "40045" }, { "ip": "192.168.1.2"} ]` |
  | `block_exploit` | `bool`                  | Enable to block common exploits                                                   |
  | `websocket`     | `bool`                  | Enable to support websocket, useful for socket.io based applications              |

- If you have obtained a SSL certificate and want to enable it, include the following params:

  | Parameter       | Type     | Description                                                                        |
  | :-------------- | :------- | :--------------------------------------------------------------------------------- |
  | `enableSSL`     | `bool`   | Enable to listen for `https`                                                       |
  | `forceSSL`      | `bool`   | Enable to force redirect `http` requests to `https`                                |
  | `http2`         | `bool`   | Enable to support `http2`                                                          |
  | `HSTS`          | `bool`   | Enable for strict transport security                                               |
  | `ssl_cert_path` | `string` | Absolute path to the `ssl certificate` file. **Required** if `enableSSL` is `true` |
  | `ssl_key_path`  | `string` | Absolute path to the `ssl key` file. **Required** if `enableSSL` is `true`         |

  ```
  curl -X POST http://your-machine-ip/api/create
   -H 'Content-Type: application/json'
   -H 'Authorization: Bearer <api_key>'
   -d '{"domain": "example.com", "type":"reverse_proxy", "ips": [{"ip": "localhost", "port": "3000"}], "block_exploit": true"}'
  ```

- Returns:

  ```JSON
  {"Success":"example.com added successfully"}
  ```

### Update Host

- Params are similar as of [**Add New Host**](#add-new-host)
- **Endpoint:** `POST /api/update`

  ```
  curl -X POST http://your-machine-ip/api/update
  -H 'Content-Type: application/json'
  -H 'Authorization: Bearer <api_key>'
  -d '{"domain": "example.com", "type":"static", "static_path": "/etc/html", "block_exploit": true"}'
  ```

- Returns:

  ```JSON
  {"Success":"example.com record updated successfully"}
  ```

### Disable Host

- Temporarily disable a HOST while preserving all of its configuration
- **Endpoint:** `POST /api/disable`

  | Parameter | Type     | Description                                       |
  | :-------- | :------- | :------------------------------------------------ |
  | `domain`  | `string` | **Required**. The domain that you want to disable |

  ```
  curl -X POST http://your-machine-ip/api/disable
  -H 'Content-Type: application/json'
  -H 'Authorization: Bearer <api_key>'
  -d '{"domain": "example.com"}'
  ```

- Returns:

  ```JSON
  {"Success":"example.com is disabled!"}
  ```

### Enable Host

- To enable previously disabled a HOST
- **Endpoint:** `POST /api/enable`

  | Parameter | Type     | Description                                      |
  | :-------- | :------- | :----------------------------------------------- |
  | `domain`  | `string` | **Required**. The domain that you want to enable |

  ```
  curl -X POST http://your-machine-ip/api/enable
  -H 'Content-Type: application/json'
  -H 'Authorization: Bearer <api_key>'
  -d '{"domain": "example.com"}'
  ```

- Returns:

  ```JSON
  {"Success":"example.com is enabled!"}
  ```

### Delete Host

- **Endpoint:** `POST /api/delete`

  | Parameter | Type     | Description                                      |
  | :-------- | :------- | :----------------------------------------------- |
  | `domain`  | `string` | **Required**. The domain that you want to delete |

  ```
  curl -X POST http://your-machine-ip/api/delete
  -H 'Content-Type: application/json'
  -H 'Authorization: Bearer <api_key>'
  -d '{"domain": "example.com"}'
  ```

- Returns:

  ```JSON
  {"Success":"example.com removed successfully"}
  ```

---

## Web Interface Demo:

**Add Hosts:**

<img src="https://raw.githubusercontent.com/Sajjal/Nginx-Proxy-Manager-Lite/main/frontend/public/add_new_host.png">

---

**View Hosts:**

<img src="https://raw.githubusercontent.com/Sajjal/Nginx-Proxy-Manager-Lite/main/frontend/public/list_host.png">

---

With Love,

**Sajjal**
