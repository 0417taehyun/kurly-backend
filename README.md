# Market Kurly

> 이커머스 사이트 [ Market Kurly ] clone project

## Table of contents

- [General info](#general-info)
- [Modeling](#modeling)
- [Technologies](#technologies)
- [Features](#features)

## General info

- 개발기간 : 2020. 10. 05 - 2020. 10. 23
- 팀원 : Front-end(강예지, 박진아, 오상구, 이조은) Back-end(김현우, 이태현)

## Modeling

- 사이트 : https://aquerytool.com:443/aquerymain/index/?rurl=19fdfe33-b13f-4f70-bc81-0aec080719a0&
- 비밀번호 : 56ti0q

## Technologies

### Tools

- Git(Control Commit history by Squash and Rebase)
- [Trello](https://trello.com/b/BCxUJ4IK)
- AWS
- Docker
- [PostMan](https://documenter.getpostman.com/view/12446418/TVejiAN3)

### Back-End

- Python
- Django Web Framework
- CORS headers
- Selenium
- MySQL
- Redis
- Elasticsearch
- Bcrypt, JWT
- Google Social Login
- RESTful API
- Docker
- AWS (EC2, RDS, Elasticache, Elasticsearch Service)

## Features

### 담당 역할

#### 이태현

- **Beautiful Soup**과 **Selenium**을 활용한 동적 페이지 크롤링
- Python 스크립트를 통한 **MySQL 데이터 베이스** 구축
- `**request**` 와 `**Q**` 를 통한 여러 필터가 적용 되는 **하나의 RESTful API** 구현
- `**POST**` , `**GET**` , `**PETCH**` , `**DELETE**` 메서드를 사용하여 장바구니 **CRUD API** 구현
- `**prefetch related**` , `**annotate**` 와 `**F**` , `**aggregate**` 와 `**Sum**`  등의 **ORM 문법** 사용으로 코드 가독성, 효율성 증대
- **AWS RDS**와 **EC2**를 활용한 서버 배포