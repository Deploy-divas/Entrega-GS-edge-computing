# CitizenTech IoT — Leitor RFID de Audiodescrição

## Integrantes:
* Amanda Silva da Mata – 572585 

* Beatriz Mantovani da Cruz – 573824 

* Laura Sampaio Neves - 570802 

## Links:

Vídeo: https://www.youtube.com/watch?v=CrMfv8VgcGA <br>
Simulador Wokwi: https://wokwi.com/projects/479949163191789569

Sistema IoT de acessibilidade que identifica objetos via tags RFID usando um ESP32, registra as leituras em uma API FastAPI hospedada na Azure com MongoDB/FIWARE e converte os dados em audiodescrição em tempo real por meio de um dashboard web.

---

## Arquitetura do Projeto

1. **Dispositivo IoT (Wokwi / ESP32):** Lê tags RFID (MFRC522), exibe feedback em um display LCD 16x2 I2C e envia requisições HTTP para a API.
2. **Backend (Azure VM + Docker):** API em Python (FastAPI) integrada ao MongoDB e infraestrutura FIWARE (Orion Context Broker).
3. **Dashboard Web (`dashboard.html`):** Interface em HTML + Tailwind CSS que exibe métricas, histórico de leituras e cadastro de novas tags.

---

## Pré-requisitos

* Conta no [Wokwi](https://wokwi.com/) (para simulação do ESP32)
* Docker e Docker Compose (na VM da Azure ou ambiente local)
* Postman ou Insomnia (opcional, para testes manuais)

---

## 1. Subindo o Backend (API + Banco de Dados)

Acesse a VM via SSH e navegue até a pasta do projeto:

```bash
cd ~/entregaGS

// Suba os contêineres com o Docker Compose:

sudo docker compose up -d --build

// Verifique se a API e o MongoDB estão ativos:

sudo docker ps
```

A documentação interativa estará disponível em:
http://158.23.58.132:8000/docs

## 2. Configurando o Simulador no Wokwi (ESP32)
Ligações dos Pinos
LCD 16x2 I2C: SDA -> Pino 21 | SCL -> Pino 22 | VCC -> 3V3/5V | GND -> GND

Leitor RFID (MFRC522): SS (SDA) -> Pino 5 | RST -> Pino 4 | SCK -> 18 | MOSI -> 23 | MISO -> 19

Configuração no Código C++
No topo do código do Wokwi, confirme se as URLs apontam para o IP da API:
```
const char* url_api_python = "http://158.23.58.132:8000/api/v1/leituras";
const char* url_api_itens  = "http://158.23.58.132:8000/api/v1/itens";
```

Inicie a simulação. O display LCD exibirá "Sistema pronto, Aproxime a tag" após a conexão com o Wi-Fi.


## 3. Como Cadastrar Tags (Itens)
- Pelo Serial Monitor do Wokwi
Com a simulação rodando, digite no terminal do Wokwi seguindo o padrão CADASTRAR,TAG,CATEGORIA,NOME e pressione Enter:

```Plaintext
CADASTRAR,99887766,alimento,Caixa de Leite
```

- Pelo Dashboard Web 
Abra o arquivo dashboard.html no navegador.

No painel Cadastrar Nova Tag, preencha: Tag ID, Categoria, Nome do objeto e Texto da audiodescrição.

Clique em Salvar Tag no Banco.

## Principais Endpoints da API
| Método | Rota | Descrição |
|--------|------|----------|
| POST | /api/v1/itens | Cadastra uma nova tag com metadados e audiodescrição |
| GET | /api/v1/itens |  Lista todos os itens cadastrados no MongoDB |
| POST | /api/v1/leituras | Registra uma leitura enviada pelo ESP32 e cruza com o item |
| GET | /api/v1/leituras | Retorna o histórico de leituras para o dashboard |
