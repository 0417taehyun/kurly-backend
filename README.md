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

- **`annotate`** , **`Value`** , **`Count`** 를 활용하여 **임시 필드**를 만들어 필요한 데이터 값을 효율적으로 창출
- Json 데이터를 Body로 받아 **다수의 필터**가 적용되는 **하나의 RESTful API** 구현
- **AWS Elasticache Redis**를 활용한 **대용량 데이터 캐싱**을 통해 처리 속도 향상
- **AWS Elasticsearch Service**와 **NGram Tokenizer**, 유니코드를 통한 **한글 음운 분리 및 키 맵핑**(한영키 오타)을 통한 정확도 높은 **검색 기능** 구현
- **Docker**, **AWS RDS**와 **EC2**를 활용한 서버 배포