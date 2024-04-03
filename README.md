# diplomski

Kafka + protokol bufferi umjesto slanja stringom

### Dokumentacija

- [GitHub repo koji implementira protokol buffere u Kafka komunikaciji](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py)
- [Protobuf dokumentacija](https://protobuf.dev/)

# Izvještaj sastanka (2023-11-10)

## Problem / pitanje

- Koliko bi se mogla ubrzati komunikacija u Kafka producer-consumer okruženju
  ukoliko se poruke ne šalju preko JSONa, nego na drugačiji, serijalizirani način?
- Tu u igru dolaze protokol bufferi

## Protokol bufferi

Izvor:

- [protobuf.dev](https://protobuf.dev/)
- [protobuf sa kafkom u pythonu](https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/protobuf_producer.py)

Protocol bufferi...

- sadrže strukturu objekta
- na temelju te strukture generirao bi se Kafka producer i consumer
- Kafka topic ne bi spremao podatke u JSONu i komunicirao sa stringovima
- za komunikaciju bi se koristili serijalizirani objekti

## Svrha

Postići neku vrstu Swaggera za Kafka messaging

Primjer strukture i rasporeda repozitorijâ:

1. Repo sa Protobuf objektima
2. Servis koji produca informacije
3. Servis koji consuma informacije

Automatizacija obavještavanja - čim se updejta repo sa protobuf objektima, može se svim servisima dati obavijest 'Imamo nove objekte na Kafki'.

# Testiranje

- implementirati običnu strukturu, JSONom
- implementirati protobuf strukturu

## Usporediti...

- kako se obje strukture ponašaju u komunikaciji pod raznim parametrima
- koja je optimalnija?

### Parametri...

- za, primjerice, 1000, 10000, 1 000 000 poruka?
- za velike i male poruke? kombinaciju?

### Resursi...

- Koliko se mrežnih resursa pritom potrošilo?
- Koliko je to trajalo?
- Koliko je procesorske snage potrošila serijalizacija i deserijalizacija navedenih poruka?
