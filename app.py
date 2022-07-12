from flask import Flask, render_template
import pandas as pd

#dados
lista_jogos = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogos')
lista_jogos['data'] = pd.to_datetime(lista_jogos['data']).dt.date
lista_clubes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Clubes')
lista_campeoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Campeões')
lista_artilharia = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Artilharia')
lista_jogadores = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogadores')
lista_observacoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Observações')
lista_competicoes = pd.DataFrame(
    columns=['codigo', 'competicao'],
    data = ([
        ['ne', 'Copa do Nordeste'],
        ['br1', 'Campeonato Brasileiro Série A1']
    ]))

#funções
def partidas(competicao = 0, ano = 0, grupo = 0, fase = 0, clube = 0):

    jogos = pd.merge(left = lista_jogos, right = lista_observacoes, left_on='id_jogo', right_on='id_jogo', how='left')

    jogos = pd.DataFrame({
        'ID': jogos['id_jogo'],
        'Competição': jogos['competicao'],
        'Ano': jogos['ano'],
        'Data': jogos['data'],
        'Horário': jogos['horario'],
        'Grupo': jogos['grupo'],
        'Fase': jogos['fase'],
        'Rodada': jogos['rodada'],
        'Mandante': jogos['mandante'],
        'Placar': jogos['gol_m'].astype(str) + '-' + jogos['gol_v'].astype(str),
        'Visitante': jogos['visitante'],
        'Local': jogos['local'],
        'Obs': jogos['obs']
    })

    jogos = jogos.where(pd.notnull(jogos), '')

    #arguments
    jogos = jogos[jogos['Competição'] == competicao] if competicao != 0 else jogos
    jogos = jogos[jogos['Ano'] == ano] if ano != 0 else jogos    
    jogos = jogos[jogos['Grupo'] == grupo] if grupo != 0 else jogos
    jogos = jogos[jogos['Fase'] == fase] if fase != 0 else jogos
    jogos = jogos[jogos['ID'].str.contains(clube)] if clube != 0 else jogos
    #jogos = jogos.sort_values(['Data'], ascending = [False]) if clube != 0 else jogos.sort_values(['Data'], ascending = [True])

    return jogos

def classificacao(competicao = 0, ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0):
    clasf1 = pd.DataFrame({
        'id_jogo': lista_jogos['id_jogo'],
        'Ano': lista_jogos['ano'],
        'Competição': lista_jogos['competicao'],
        'Grupo': lista_jogos['grupo'],
        'Fase': lista_jogos['fase'],
        'Estádio': lista_jogos['local'],
        'Clube': lista_jogos['mandante'],
        'Pts': 0,
        'J': 1,
        'V': 0,
        'E': 0,
        'D': 0,
        'GP': lista_jogos['gol_m'],
        'GC': lista_jogos['gol_v'],
        'Saldo': lista_jogos['gol_m'] - lista_jogos['gol_v'],
    })
    clasf2 = pd.DataFrame({
        'id_jogo': lista_jogos['id_jogo'],
        'Ano': lista_jogos['ano'],
        'Competição': lista_jogos['competicao'],
        'Grupo': lista_jogos['grupo'],
        'Fase': lista_jogos['fase'],
        'Estádio': lista_jogos['local'],
        'Clube': lista_jogos['visitante'],
        'Pts': 0,
        'J': 1,
        'V': 0,
        'E': 0,
        'D': 0,
        'GP': lista_jogos['gol_v'],
        'GC': lista_jogos['gol_m'],
        'Saldo': lista_jogos['gol_v'] - lista_jogos['gol_m'],
    })   

    classificacao = pd.concat([clasf1, clasf2])
    
    classificacao.loc[classificacao['GP'] > classificacao['GC'], 'V'] = 1
    classificacao.loc[classificacao['GP'] == classificacao['GC'], 'E'] = 1
    classificacao.loc[classificacao['GP'] < classificacao['GC'], 'D'] = 1
    classificacao.loc[classificacao['GP'] > classificacao['GC'], 'Pts'] = vitoria
    classificacao.loc[(classificacao['GP'] == classificacao['GC']) & (classificacao['GP'] + classificacao['GC'] == 0), 'Pts'] = empate_sem_gols
    classificacao.loc[(classificacao['GP'] == classificacao['GC']) & (classificacao['GP'] + classificacao['GC'] > 0), 'Pts'] = empate_com_gols
    classificacao.loc[classificacao['GP'] < classificacao['GC'], 'Pts'] = 0

    #argumentos
    classificacao = classificacao[classificacao['Competição'] == competicao] if competicao != 0 else classificacao
    classificacao = classificacao[classificacao['Ano'] == ano] if ano != 0 else classificacao
    classificacao = classificacao[classificacao['Grupo'] == grupo] if grupo != 0 else classificacao
    classificacao = classificacao[classificacao['Fase'] == fase] if fase != 0 else classificacao
    classificacao = classificacao[classificacao['Clube'].str.contains(clube)] if clube != 0 else classificacao
    classificacao = classificacao.sort_values(['Pts', 'Saldo'], ascending = [False, False])
    classificacao = classificacao.groupby(['Clube']).sum().reset_index().sort_values(['Pts', 'V', 'Saldo'], ascending = [False, False, False]).drop(columns=['Ano']).reset_index().drop('index', axis=1)
    classificacao.insert(0, 'Pos', classificacao.index + 1)
    return classificacao

def participacoes(ano, competicao):
    lista_mundanca_clube = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Mudanças')
    lista_jogos2 = lista_jogos[lista_jogos['competicao'] == competicao]
    lista_jogos2 = lista_jogos[lista_jogos['competicao'] == competicao]
    lista_mandantes = lista_jogos2[['mandante', 'ano']].groupby(['mandante', 'ano']).sum().reset_index()
    lista_mandantes.columns = ['clube', 'ano']
    lista_visitantes = lista_jogos2[['visitante', 'ano']].groupby(['visitante', 'ano']).sum().reset_index()
    lista_visitantes.columns = ['clube', 'ano']
    participacoes = pd.concat([lista_mandantes, lista_visitantes]).groupby(['clube', 'ano']).sum().reset_index()

    clubes_participacoes = participacoes[participacoes['ano'] <= ano]
    participacoes = participacoes[participacoes['ano'] == ano]
    n_participacoes = pd.DataFrame(clubes_participacoes['clube'].value_counts()).reset_index()
    participacoes = pd.merge(left=participacoes, right=n_participacoes, left_on='clube', right_on='index')
    participacoes = participacoes.drop(columns=['ano', 'index'])
    participacoes.columns = ['clube', 'participações']    
    participacoes = pd.merge(left=participacoes, right=lista_clubes, left_on='clube', right_on='clube', how='left').sort_values(['clube'])
    participacoes = pd.merge(left=participacoes, right=lista_mundanca_clube, left_on='completo', right_on='clube', how='left').fillna('')
    participacoes = pd.DataFrame({
        'Clube': participacoes['clube_x'],
        'Completo': participacoes['completo'],
        'Participações': participacoes['participações'],
        'Slug': participacoes['slug'],
        'Obs': participacoes['obs']
    })
    return participacoes

def campeao(ano, competicao):
    lista_campeoes2 = lista_campeoes[lista_campeoes['competicao'] == competicao]
    lista_campeoes2 = lista_campeoes2[lista_campeoes2['ano'] <= ano]
    clube_campeao = lista_campeoes2[lista_campeoes2['ano'] == ano]
    lista_campeoes2['titulos'] = 1 
    lista_campeoes2 = lista_campeoes2.groupby(['clube']).sum().reset_index().drop(columns=['ano'])
    clube_campeao = pd.merge(left=clube_campeao, right=lista_campeoes2, left_on='clube', right_on='clube')[['clube', 'titulos']]
    return pd.merge(left=clube_campeao, right=lista_clubes, left_on='clube', right_on='clube')[['clube', 'completo', 'titulos', 'slug']]

def artilharia(competicao = 0, ano = 0):
    artilharia = pd.merge(left = lista_artilharia, right = lista_jogos, left_on='id_jogo', right_on='id_jogo')
    artilharia = pd.merge(left = artilharia, right = lista_jogadores, left_on='jogador', right_on='jogador')
    artilharia['gol'] = 1
    artilharia2 = artilharia[['id_jogo', 'jogador', 'clube', 'tempo', 'min', 'ano', 'competicao', 'apelido', 'gol']]
    artilharia2 = artilharia2[artilharia2['ano'] == ano]
    artilharia2 = artilharia2[artilharia2['competicao'] == competicao]
    artilharia2 = artilharia2.groupby(['apelido', 'jogador', 'clube']).sum().reset_index().drop(columns=['ano']).sort_values(['gol'], ascending = [False])
    artilharia2.columns = ['Artilheiro', 'Jogador', 'Clube', 'Gols']
    return artilharia2

def dados(competicao, ano):
    lista_jogos2 = lista_jogos[lista_jogos['competicao'] == competicao]
    lista_jogos2 = lista_jogos2[lista_jogos2['ano'] == ano]
    data = pd.DataFrame(lista_jogos2.sort_values(['data'], ascending = [True])['data'])
    inicio = str(data.head(1).to_string().strip()).split('  ')[1]
    final = str(data.tail(1).to_string().strip()).split('  ')[1]

    dados = {
        'Participantes': len(participacoes(ano, competicao)),
        'Nº de partidas': classificacao('Copa do Nordeste', ano).sum()['J'],
        'Total de gols': classificacao('Copa do Nordeste', ano).sum()['GP'],
        'Média de gols': "{:.2f}".format(classificacao('Copa do Nordeste', ano).sum()['GP'] / classificacao('Copa do Nordeste', ano).sum()['J']),
        'Período': [inicio, final]
        }
    return dados

def clube_info(clube_completo):
    clube = lista_clubes[lista_clubes['slug'] == clube_completo]
    return clube

def partida_dados(id):
    partida = lista_jogos[lista_jogos['id_jogo'] == id]
    return partida

#flask app
app = Flask(__name__)

## competições (copa do nordeste)
@app.route('/')
@app.route('/competicoes/')
@app.route('/competicoes/ne/')
@app.route('/clubes/')
def index():  
    return render_template('home.html',
        title = 'NE Dados FC',
        lista_clubes = lista_clubes.to_dict('records'),
    )

@app.route('/competicoes/<sigla_competicao>/<edicao>')
def ne(edicao, sigla_competicao):

    # parâmetros
    ano = int(edicao)

    # pontuação
    if ano == 1994:
        pts_empate_sem_gols = 1
        pts_empate_com_gols = 2
        pts_vitoria = 3
    else:
        pts_empate_sem_gols = 1
        pts_empate_com_gols = 1
        pts_vitoria = 3
    
    competicao = lista_competicoes[lista_competicoes['codigo'] == sigla_competicao]['competicao'][0]

    return render_template('/ne.html',

        title = competicao,
        edicao=ano,

        # dados
        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),
        regulamento = '',
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records'),

        # fase preliminar
        fase_preliminar_jogos = partidas(competicao, ano, 'Único', 'Fase preliminar').to_dict('records'),

        # primeira fase
        primeira_fase_jogos = partidas(competicao, ano, 'Único', 'Primeira fase').to_dict('records'),
        primeira_fase_classificacao = classificacao(
            competicao, ano, 'Único', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_a_jogos = partidas(competicao, ano, 'Grupo A', 'Primeira fase').to_dict('records'),
        grupo_a_classificacao = classificacao(
            competicao, ano, 'Grupo A', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_b_jogos = partidas(competicao, ano, 'Grupo B', 'Primeira fase').to_dict('records'),
        grupo_b_classificacao = classificacao(
            competicao, ano, 'Grupo B', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),   
        
        grupo_c_jogos = partidas(competicao, ano, 'Grupo C', 'Primeira fase').to_dict('records'),
        grupo_c_classificacao = classificacao(
            competicao, ano, 'Grupo C', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_d_jogos = partidas(competicao, ano, 'Grupo D', 'Primeira fase').to_dict('records'),
        grupo_d_classificacao = classificacao(
            competicao, ano, 'Grupo D', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_e_jogos = partidas(competicao, ano, 'Grupo E', 'Primeira fase').to_dict('records'),
        grupo_e_classificacao = classificacao(
            competicao, ano, 'Grupo E', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_f_jogos = partidas(competicao, ano, 'Grupo F', 'Primeira fase').to_dict('records'),
        grupo_f_classificacao = classificacao(
            competicao, ano, 'Grupo F', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        # segunda fase / mata-matas
        grupo_e2_jogos = partidas(competicao, ano, 'Grupo E', 'Segunda fase').to_dict('records'),
        grupo_e2_classificacao = classificacao(
            competicao, ano, 'Grupo E', 'Segunda fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),
        
        grupo_f2_jogos = partidas(competicao, ano, 'Grupo F', 'Segunda fase').to_dict('records'),
        grupo_f2_classificacao = classificacao(
            competicao, ano, 'Grupo F', 'Segunda fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        of=partidas(competicao, ano, 0, 'Oitavas de final').to_dict('records'),
        qf=partidas(competicao, ano, 0, 'Quartas de final').to_dict('records'),
        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),        
    )

## clubes
@app.route('/clubes/<clube>')
def clubes(clube):
    slug = clube_info(clube)['slug'].iloc[0]
    nome_completo = clube_info(clube)['completo'].iloc[0]
    nome_curto = clube_info(clube)['clube'].iloc[0]
    escudo = clube_info(clube)['slug'].iloc[0]
    fundacao = clube_info(clube)['fundacao'].iloc[0]
    cidade = clube_info(clube)['cidade'].iloc[0]
    estado = clube_info(clube)['estado'].iloc[0]

    return render_template('/clubes/clube.html',
        slug = slug,
        clube = nome_completo,
        nome_curto = nome_curto,
        escudo = escudo,
        fundacao = fundacao,
        cidade = cidade,
        estado = estado,
        geral = classificacao(competicao = 0, ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = nome_curto).to_dict('records'),
        copa_ne = classificacao(competicao = 'Copa do Nordeste', ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = nome_curto).to_dict('records'),
    )

if __name__ == '__main__':
    app.run(debug=True) #debug=True, port=8080