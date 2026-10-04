<div align="center">
  <img alt="Square Cloud Banner" src="https://cdn.squarecloud.app/png/github-readme.png">
</div>

> 📌 **Note:** This README is written in Portuguese because this project was created as part of a YouTube tutorial in Portuguese.

<h1 align="center">giveaway-bot</h1>
<p align="center">Um bot de sorteios para Discord criado com discord.py.</p>

---

Este projeto é um **bot de sorteios** para Discord desenvolvido durante um vídeo no canal do YouTube da **Square Cloud**, demonstrando como construir um sistema completo de sorteios usando **discord.py**.

O bot permite criar sorteios com duração e número de vencedores configuráveis, encerrando-os automaticamente e anunciando os vencedores diretamente no canal.

O vídeo que originou este projeto está disponível no YouTube:
https://youtu.be/naDV10shTFQ

---

## ☁️ Como hospedar na Square Cloud

Nunca usou a Square Cloud? Siga os passos abaixo, na ordem: você vai criar uma conta, escolher um plano, criar o bot no Discord e enviar o projeto.

### 1️⃣ Crie sua conta na Square Cloud

Cadastre-se na [página de cadastro da Square Cloud](https://squarecloud.app/pt-br/signup) com o seu e-mail.

### 2️⃣ Escolha um plano

A hospedagem na Square Cloud precisa de um plano ativo, e o envio do passo 5 pede um, então escolha agora.

Este bot usa só **256 MB de RAM**: o **[plano Hobby](https://squarecloud.app/pt-br/pricing)** é suficiente e ainda sobra espaço para outros bots. Compare todos os planos e preços na [página de planos](https://squarecloud.app/pt-br/pricing).

### 3️⃣ Crie o bot no Discord

1. No [Discord Developer Portal](https://discord.com/developers/applications), clique em **New Application** e dê um nome ao bot.
2. Na aba **Bot**, clique em **Reset Token** e copie o token. Guarde-o em segredo: ele controla o seu bot.
3. Na mesma aba, em **Privileged Gateway Intents**, ative **Presence Intent**, **Server Members Intent** e **Message Content Intent**.
4. Convide o bot para o seu servidor: em **OAuth2 > URL Generator**, marque `bot` e `applications.commands`, escolha as permissões e abra o link gerado.

### 4️⃣ Prepare o projeto

1. No topo desta página, clique em **Code > Download ZIP** e extraia o arquivo.
2. Abra a pasta extraída, selecione **todos os arquivos dentro dela** e compacte-os em um novo `.zip`. Compacte os arquivos, não a pasta: o `squarecloud.app` precisa ficar na raiz do zip.

### 5️⃣ Envie para a Square Cloud

1. Acesse a [página de upload da Square Cloud](https://squarecloud.app/pt-br/dashboard/new).
2. Selecione a opção de **zip** e envie o arquivo que você criou.
3. Abra **Configuração avançada** e adicione as variáveis de ambiente:
   - `TOKEN`: o token do bot (passo 3)
   - `CARGO_MANAGER`: o ID do cargo que pode criar e cancelar sorteios
4. Clique em **Deploy**.

![Enviando um projeto para a Square Cloud](https://cdn.squarecloud.app/docs/articles/dashboard/uploading.gif)

> 💡 **Como copiar um ID no Discord:** ative o **Modo de desenvolvedor** em **Configurações > Avançado**, clique com o botão direito no cargo ou canal e escolha **Copiar ID**.

### 6️⃣ Teste o bot

Com o cargo definido em `CARGO_MANAGER`, use `/sorteio` em um canal do seu servidor e `/cancelar_sorteio` para cancelá-lo. Se o bot não responder, abra a aplicação no [dashboard da Square Cloud](https://squarecloud.app/pt-br/dashboard) e confira os logs.

📖 Mais detalhes no [guia de bots do Discord](https://docs.squarecloud.app/pt-br/tutorials/bots/discord) da documentação da Square Cloud.

---

## 💻 Rodando no seu computador

1. Instale as dependências: `pip install -r requirements.txt`
2. Crie um arquivo `.env` com as variáveis `TOKEN` e `CARGO_MANAGER`.
3. Rode o bot: `python main.py`

Requer Python 3.10 ou mais recente.
