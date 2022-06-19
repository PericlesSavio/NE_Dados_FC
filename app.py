from flask import Flask, render_template
import pandas as pd

#base
lista_jogos = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogos')
lista_jogos['data'] = pd.to_datetime(lista_jogos['data']).dt.date
lista_clubes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Clubes')
lista_campeoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Campeões')
lista_artilharia = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Artilharia')
lista_jogadores = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogadores')
lista_observacoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Observações')

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
    classificacao = classificacao[classificacao['id_jogo'].str.contains(clube)] if clube != 0 else classificacao
    classificacao = classificacao.sort_values(['Pts', 'Saldo'], ascending = [False, False])
    classificacao = classificacao.groupby(['Clube']).sum().reset_index().sort_values(['Pts', 'V', 'Saldo'], ascending = [False, False, False]).drop(columns=['Ano']).reset_index().drop('index', axis=1)
    classificacao.insert(0, 'Pos', classificacao.index + 1)
    return classificacao

def participacoes(ano, competicao):
    lista_jogos2 = lista_jogos[lista_jogos['competicao'] == competicao]
    participacoes = lista_jogos2.groupby(['mandante', 'ano']).sum().reset_index().drop(columns=['gol_m', 'gol_v'])
    clubes_participacoes = participacoes[participacoes['ano'] <= ano]
    participacoes = participacoes[participacoes['ano'] == ano]
    participacoes = lista_jogos2.groupby(['mandante', 'ano']).sum().reset_index().drop(columns=['gol_m', 'gol_v'])
    clubes_participacoes = participacoes[participacoes['ano'] <= ano]
    participacoes = participacoes[participacoes['ano'] == ano]
    n_participacoes = pd.DataFrame(clubes_participacoes['mandante'].value_counts()).reset_index()
    participacoes = pd.merge(left=participacoes, right=n_participacoes, left_on='mandante', right_on='index')
    participacoes = participacoes.drop(columns=['ano', 'index'])
    participacoes.columns = ['Clube', 'Participações']    
    return participacoes.sort_values(['Clube'])

def campeao(ano, competicao):
    lista_campeoes2 = lista_campeoes[lista_campeoes['competicao'] == competicao]
    lista_campeoes2 = lista_campeoes2[lista_campeoes2['ano'] <= ano]
    clube_campeao = lista_campeoes[lista_campeoes['ano'] == ano]
    lista_campeoes2['titulos'] = 1 
    lista_campeoes2 = lista_campeoes2.groupby(['clube']).sum().reset_index().drop(columns=['ano'])
    clube_campeao = pd.merge(left=clube_campeao, right=lista_campeoes2, left_on='clube', right_on='clube')[['clube', 'titulos']]
    return pd.merge(left=clube_campeao, right=lista_clubes, left_on='clube', right_on='clube')[['clube', 'completo', 'titulos', 'escudo']]

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

def clube(clube_completo):
    clube = lista_clubes[lista_clubes['completo'] == clube_completo]
    return clube

def partida_dados(id):
    partida = lista_jogos[lista_jogos['id_jogo'] == id]
    return partida




app = Flask(__name__)

@app.route('/')
@app.route('/competicoes/')
@app.route('/competicoes/ne/')
def index():    
    return render_template('home.html',
        title = 'NE Dados FC'
    )


@app.route('/competicoes/ne/1994')
def ne1994():
    url = 'ne'
    ano = 1994
    competicao = 'Copa do Nordeste'
    pts_empate_sem_gols = 1
    pts_empate_com_gols = 2
    pts_vitoria = 3

    return render_template('/'+url+'/ne.html', #'/'+url+'/'+str(ano)+'.html',
        url = url,
        title = competicao,
        edicao=ano,

        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),

        regulamento = 'Os 16 clubes se dividiriam em 4 grupos com 4 participantes cada. Os 2 melhores classificados de cada grupo avançariam para as quartas-de-final. Os vencedores para as semifinais e, por fim, para a grande final. Todas as fases teriam apenas jogos de ida. Houve uma única alteração nas regras de pontuação: empate sem gols valeria um e com gols valeria dois pontos.',

        grupo_a_classificacao = classificacao(
            competicao, ano, 'Grupo A', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_b_classificacao = classificacao(
            competicao, ano, 'Grupo B', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_c_classificacao = classificacao(
            competicao, ano, 'Grupo C', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_d_classificacao = classificacao(
            competicao, ano, 'Grupo D', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_a_jogos = partidas(competicao, ano, 'Grupo A', 'Primeira fase').to_dict('records'),
        grupo_b_jogos = partidas(competicao, ano, 'Grupo B', 'Primeira fase').to_dict('records'),
        grupo_c_jogos = partidas(competicao, ano, 'Grupo C', 'Primeira fase').to_dict('records'),
        grupo_d_jogos = partidas(competicao, ano, 'Grupo D', 'Primeira fase').to_dict('records'),

        qf=partidas(competicao, ano, 0, 'Quartas de final').to_dict('records'),
        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),
        
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records'),
    )

@app.route('/competicoes/ne/1997')
def ne1997():
    url = 'ne'
    ano = 1997
    competicao = 'Copa do Nordeste'
    pts_empate_sem_gols = 1
    pts_empate_com_gols = 1
    pts_vitoria = 3

    return render_template('/'+url+'/ne.html',
        url = url,
        title = competicao,
        edicao=ano,

        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),

        regulamento = 'O campeonato seria disputado em sistema mata-mata, começando com oitavas-de-final. Fortaleza e Ceará disputariam a fase preliminar para decidir qual time entraria de fato no certame.',

        of=partidas(competicao, ano, 0, 'Oitavas de final').to_dict('records'),
        qf=partidas(competicao, ano, 0, 'Quartas de final').to_dict('records'),
        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),
        
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records'),
    )

@app.route('/competicoes/ne/1998')
def ne1998():
    url = 'ne'
    ano = 1998
    competicao = 'Copa do Nordeste'
    pts_empate_sem_gols = 1
    pts_empate_com_gols = 1
    pts_vitoria = 3

    return render_template('/'+url+'/ne.html', #'/'+url+'/'+str(ano)+'.html',
        url = url,
        title = competicao,
        edicao=ano,

        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),

        regulamento = 'Os 16 clubes se dividiriam em 4 grupos de 4 e, dentro de cada grupo, se enfrentariam em jogos de ida e volta. Os 2 melhores classificados de cada grupo avançariam para a Segunda Fase e formariam outros 2 grupos de 4, também se enfrentando em jogos de ida e volta. Assim, 2 times se classificariam, 1 por grupo, e fariam a final para decidir o título do campeonato.',

        grupo_a_classificacao = classificacao(
            competicao, ano, 'Grupo A', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_b_classificacao = classificacao(
            competicao, ano, 'Grupo B', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_c_classificacao = classificacao(
            competicao, ano, 'Grupo C', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_d_classificacao = classificacao(
            competicao, ano, 'Grupo D', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_a_jogos = partidas(competicao, ano, 'Grupo A', 'Primeira fase').to_dict('records'),
        grupo_b_jogos = partidas(competicao, ano, 'Grupo B', 'Primeira fase').to_dict('records'),
        grupo_c_jogos = partidas(competicao, ano, 'Grupo C', 'Primeira fase').to_dict('records'),
        grupo_d_jogos = partidas(competicao, ano, 'Grupo D', 'Primeira fase').to_dict('records'),

        grupo_e2_classificacao = classificacao(
            competicao, ano, 'Grupo C', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_f2_classificacao = classificacao(
            competicao, ano, 'Grupo D', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),
        grupo_e2_jogos = partidas(competicao, ano, 'Grupo C', 'Primeira fase').to_dict('records'),
        grupo_f2_jogos = partidas(competicao, ano, 'Grupo D', 'Primeira fase').to_dict('records'),

        qf=partidas(competicao, ano, 0, 'Quartas de final').to_dict('records'),
        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),
        
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records'),
    )

@app.route('/competicoes/ne/2000')
def ne2000():
    url = 'ne'
    ano = 2000
    competicao = 'Copa do Nordeste'
    pts_empate_sem_gols = 1
    pts_empate_com_gols = 1
    pts_vitoria = 3

    return render_template('/'+url+'/ne.html', #'/'+url+'/'+str(ano)+'.html',
        url = url,
        title = competicao,
        edicao=ano,

        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),

        regulamento = 'Os 16 clubes se dividiriam em 4 grupos com 4 participantes cada. Os 2 melhores classificados de cada grupo avançariam para as quartas-de-final. Os vencedores para as semi-finais e, por fim, para a grande final. Todas as fases teriam jogos de ida e volta.',

        grupo_a_classificacao = classificacao(
            competicao, ano, 'Grupo A', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_b_classificacao = classificacao(
            competicao, ano, 'Grupo B', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_c_classificacao = classificacao(
            competicao, ano, 'Grupo C', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),        
        grupo_d_classificacao = classificacao(
            competicao, ano, 'Grupo D', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        grupo_a_jogos = partidas(competicao, ano, 'Grupo A', 'Primeira fase').to_dict('records'),
        grupo_b_jogos = partidas(competicao, ano, 'Grupo B', 'Primeira fase').to_dict('records'),
        grupo_c_jogos = partidas(competicao, ano, 'Grupo C', 'Primeira fase').to_dict('records'),
        grupo_d_jogos = partidas(competicao, ano, 'Grupo D', 'Primeira fase').to_dict('records'),

        qf=partidas(competicao, ano, 0, 'Quartas de final').to_dict('records'),
        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),
        
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records'),
    )

@app.route('/competicoes/ne/2001')
def ne2001():
    url = 'ne'
    ano = 2001
    competicao = 'Copa do Nordeste'
    pts_empate_sem_gols = 1
    pts_empate_com_gols = 1
    pts_vitoria = 3

    return render_template('/'+url+'/ne.html', #'/'+url+'/'+str(ano)+'.html',
        url = url,
        title = competicao,
        edicao=ano,

        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),

        regulamento = 'Todos os 16 clubes se enfrentariam em jogos apenas de ida, os 4 melhores classificados avançariam às semifinais, com 2 chegando à final e decidindo o título.',

        primeira_fase_jogos = partidas(competicao, ano, 0, 'Primeira fase').to_dict('records'),
        primeira_fase_classificacao = classificacao(
            competicao, ano, 0, 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),
        
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records')
    )

@app.route('/competicoes/ne/2002')
def ne2002():
    url = 'ne'
    ano = 2002
    competicao = 'Copa do Nordeste'
    pts_empate_sem_gols = 1
    pts_empate_com_gols = 1
    pts_vitoria = 3

    return render_template('/'+url+'/ne.html', #'/'+url+'/'+str(ano)+'.html',
        url = url,
        title = competicao,
        edicao=ano,

        n_participantes = dados(competicao, ano)['Participantes'],
        n_partidas = dados(competicao, ano)['Nº de partidas'],
        total_jogos = dados(competicao, ano)['Total de gols'],
        media_gols = dados(competicao, ano)['Média de gols'],
        periodo = dados(competicao, ano)['Período'],
        participantes=participacoes(ano, competicao).to_dict('records'),

        regulamento = 'Todos os 16 clubes se enfrentariam em jogos apenas de ida, os 4 melhores classificados avançariam às semifinais, com 2 chegando à final e decidindo o título.',

        primeira_fase_jogos = partidas(competicao, ano, 0, 'Primeira fase').to_dict('records'),
        primeira_fase_classificacao = classificacao(
            competicao, ano, 0, 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        sf=partidas(competicao, ano, 0, 'Semifinal').to_dict('records'),
        final=partidas(competicao, ano, 0, 'Final').to_dict('records'),
        
        campeao = campeao(ano, competicao).to_dict('records'),
        titulos = campeao(ano, competicao)['titulos'].to_string().replace("0    ", ""),        
        campanha = classificacao(
            competicao = competicao, ano = ano, grupo = 0, fase = 0, vitoria = pts_vitoria, empate_sem_gols = pts_empate_sem_gols,
            empate_com_gols = pts_empate_com_gols, clube = campeao(ano, competicao).iloc[0,0]).head(1).to_dict('records')
    )


@app.route('/competicoes/ne/1994/gols')
def test():
    url = 'NE' 
    return render_template('/'+url+'/test.html',
        title = 'Futebol Pernambucano'
    )


if __name__ == '__main__':
    app.run(debug=True) #debug=True, port=8080
