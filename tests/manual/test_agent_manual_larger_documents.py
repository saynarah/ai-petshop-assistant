
from langchain_core.documents import Document

from ai_petshop_assistant.agents.petshop_agent import PetShopAgent


def create_documents() -> list[Document]:

    documents = [

        Document(
            page_content="""
# Serviços de banho e tosa

O Pet Shop Amigo Animal oferece serviços de higiene e
cuidados estéticos para cães de pequeno, médio e grande
porte. Os atendimentos são realizados mediante agendamento
e estão sujeitos à disponibilidade da equipe.

## Banho para cães

O serviço de banho inclui aplicação de shampoo apropriado
para o animal, enxágue, secagem, escovação e limpeza
externa das orelhas. Produtos especiais podem ser
utilizados conforme orientação da equipe responsável.

Para cães de pequeno porte, como Shih Tzu, Maltês,
Yorkshire e Poodle Toy, o banho costuma ter duração
de 40 a 60 minutos. O valor básico é R$ 50.

Para cães de médio porte, como Beagle e Cocker Spaniel,
o valor básico do banho é R$ 70. O atendimento costuma
durar de 60 a 90 minutos.

Para cães de grande porte, como Golden Retriever,
Labrador e Pastor Alemão, o valor inicial é R$ 100.
O preço definitivo depende das características do pelo,
do porte do animal e das condições do serviço.

## Tosa higiênica

A tosa higiênica consiste no aparo dos pelos em regiões
que precisam de cuidados específicos de higiene.

O serviço avulso custa R$ 35 para cães de pequeno porte.
Para cães médios e grandes, o valor deve ser confirmado
pela equipe antes do atendimento.

A tosa higiênica pode ser contratada junto com o banho.
Entretanto, o pet shop não possui um preço promocional
fixo para essa combinação. Os serviços são orçados
individualmente.

## Tosa completa

A tosa completa envolve o corte dos pelos do corpo,
respeitando as características do animal e as orientações
do tutor.

O pet shop trabalha com diferentes estilos de tosa,
incluindo tosa na tesoura e tosa com máquina, conforme
a avaliação da equipe.

Não existe um valor fixo para tosa completa.
O orçamento considera raça, porte, comprimento do pelo,
presença de nós e tempo necessário para o atendimento.

## Cuidados adicionais

Animais com pelagem muito embaraçada podem precisar
de avaliação antes da execução dos serviços. Caso o
procedimento solicitado não seja adequado à condição
do animal, a equipe informará as alternativas possíveis.

O pet shop também oferece hidratação de pelagem,
mas o valor depende do produto utilizado e do porte
do cachorro.

Nenhum procedimento adicional é realizado sem
autorização do responsável pelo animal.
            """,
            metadata={
                "source": "servicos_banho_tosa",
                "category": "services"
            }
        ),

        Document(
            page_content="""
# Política de preços e orçamentos

O Pet Shop Amigo Animal utiliza uma tabela de referência
para os serviços de higiene. Os valores abaixo são
fictícios e servem como base para a elaboração de
orçamentos durante o atendimento.

## Tabela de preços

Banho para cães pequenos: R$ 50.
Banho para cães médios: R$ 70.
Banho para cães grandes: a partir de R$ 100.

Tosa higiênica avulsa para cães pequenos: R$ 35.
Tosa higiênica para cães médios e grandes:
valor sujeito à confirmação.

Tosa completa: orçamento personalizado.
Hidratação de pelagem: orçamento personalizado.

## Como solicitar um orçamento

O cliente deve informar o serviço desejado, a raça
do animal, seu porte aproximado e, quando relevante,
as características da pelagem.

Se essas informações não forem suficientes para
calcular o preço, a equipe poderá solicitar informações
adicionais antes de confirmar o orçamento.

Para serviços com preço fixo cadastrado, o atendimento
pode informar o valor diretamente ao cliente.

Para serviços com preço variável, deve ser explicado
que o valor será confirmado pela equipe após avaliação.

## Combinação de serviços

Banho e tosa higiênica podem ser realizados no mesmo
atendimento. Porém, não existe desconto automático
pela contratação de ambos.

Se um cachorro pequeno contratar banho e tosa
higiênica avulsa, os dois preços de referência
somam R$ 85.

Esse valor não representa uma promoção ou pacote
comercial. A equipe deve confirmar se os serviços
e os valores se aplicam ao animal específico.

## Descontos e promoções

O pet shop pode divulgar campanhas promocionais em
períodos específicos. Entretanto, a existência de
uma promoção deve ser confirmada na tabela vigente.

O assistente não está autorizado a oferecer descontos
que não estejam expressamente documentados.

## Formas de pagamento

O estabelecimento aceita pagamentos via Pix,
cartão de débito e cartão de crédito.

O parcelamento depende do valor total da compra
e das condições informadas pela equipe.

Nenhum pagamento deve ser considerado concluído
sem confirmação do sistema responsável.
            """,
            metadata={
                "source": "politica_precos",
                "category": "pricing"
            }
        ),

        Document(
            page_content="""
# Agendamentos e horários de atendimento

O Pet Shop Amigo Animal funciona de segunda-feira
a sábado, das 8h às 18h. O estabelecimento permanece
fechado aos domingos.

Os serviços de banho e tosa são realizados com
agendamento prévio, respeitando a disponibilidade
dos profissionais e a duração prevista de cada serviço.

## Solicitação de agendamento

Para solicitar um horário, o cliente deve informar
o serviço desejado, o nome do animal, sua raça e
a data ou período de preferência.

O atendimento pode reunir essas informações e
encaminhar a solicitação para a equipe responsável.

A existência de um horário livre não pode ser
confirmada apenas com base neste documento.

A disponibilidade real precisa ser consultada
no sistema de agenda do pet shop.

## Confirmação

Um agendamento só é considerado confirmado depois
que a equipe ou o sistema autorizado registra
a reserva e comunica sua confirmação ao cliente.

Mensagens como "vou verificar" ou "solicitação recebida"
não significam que o horário já foi reservado.

## Remarcação

O cliente pode solicitar a remarcação de um atendimento.
Para isso, deverá informar o nome do animal, o serviço
agendado e a nova data ou período desejado.

A alteração depende da confirmação da equipe e da
disponibilidade de novos horários.

Até que a remarcação seja confirmada, o horário
anterior permanece sujeito às regras do agendamento.

## Cancelamento

Cancelamentos devem ser comunicados ao pet shop com
antecedência sempre que possível.

O estabelecimento recomenda que o cliente avise
com pelo menos 24 horas de antecedência para permitir
a reorganização da agenda.

Essa recomendação não implica a existência de
uma multa automática.

## Atrasos

Em caso de atraso, a equipe deverá avaliar se
o atendimento ainda poderá ser realizado no
horário previsto.

O assistente não deve prometer atendimento imediato,
encaixes ou prioridades sem confirmação da agenda.

## Consultas e vacinas

Consultas veterinárias e serviços de vacinação
dependem da disponibilidade de profissionais
habilitados e da confirmação da equipe.

A documentação não contém uma agenda veterinária
atualizada nem autoriza marcações automáticas.
            """,
            metadata={
                "source": "agendamentos",
                "category": "appointments"
            }
        ),

        Document(
            page_content="""
# Produtos, medicamentos e atendimento veterinário

O Pet Shop Amigo Animal comercializa produtos para
animais de estimação, incluindo shampoos, escovas,
coleiras, brinquedos e determinados itens de higiene.

A disponibilidade e o preço dos produtos dependem
do estoque e da tabela comercial vigente.

## Consulta de produtos

Quando um cliente pergunta se um produto está
disponível, o atendimento deve solicitar o nome
do produto e, quando necessário, sua apresentação
ou tamanho.

O estoque precisa ser consultado no sistema
responsável antes de confirmar disponibilidade.

A presença de um produto nesta documentação não
significa que ele esteja disponível para venda.

## Medicamentos veterinários

Solicitações relacionadas a medicamentos devem ser
encaminhadas à equipe habilitada.

O assistente pode registrar o nome de um medicamento
informado pelo cliente para encaminhar a solicitação,
mas não deve indicar qual medicamento utilizar.

Informações sobre doses, tratamentos, substituições
de medicamentos e adequação clínica dependem
de avaliação por profissional veterinário.

O assistente não está autorizado a recomendar
medicamentos, interpretar sintomas ou confirmar
tratamentos.

## Vacinação

O estabelecimento pode receber solicitações de
informações sobre vacinação de cães.

A disponibilidade de vacinas, valores e horários
precisa ser confirmada com a equipe veterinária.

O assistente não deve determinar calendários
vacinais individuais nem afirmar que determinada
vacina é apropriada para um animal específico.

## Consultas veterinárias

Clientes que desejam agendar uma consulta podem
informar o nome do animal, sua espécie e o período
de preferência.

O atendimento poderá encaminhar a solicitação
à equipe responsável pelo agendamento.

O valor da consulta veterinária não está especificado
neste documento e precisa ser confirmado.

## Atendimento humano

Quando a solicitação envolver orientação clínica,
medicamentos, informações indisponíveis ou situações
que exijam autorização profissional, o atendimento
deve encaminhar o cliente a uma pessoa responsável.

Se o cliente relatar uma situação que pareça urgente,
deve ser orientado a procurar atendimento veterinário
imediatamente, sem aguardar uma resposta automática.
            """,
            metadata={
                "source": "produtos_veterinario",
                "category": "veterinary"
            }
        ),
    ]

    return documents


def main():
    agent = PetShopAgent(
        persist_directory="./data/chroma",
        chunk_size=500,
        chunk_overlap=100,
    )

    documents = create_documents()

    count = agent.add_documents(documents)

    print(f"\nDocuments loaded: {len(documents)}")
    print(f"Chunks indexed: {count}")
    print(
        "Total records in Chroma:",
        agent.vectorstore._collection.count()
    )


if __name__ == "__main__":
    main()
