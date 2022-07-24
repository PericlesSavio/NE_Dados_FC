from flask import Flask, render_template
import pandas as pd

#dados
lista_jogos = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogos')
lista_jogos['data'] = pd.to_datetime(lista_jogos['data']).dt.date
lista_clubes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Clubes')
lista_campeoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Campeões')
lista_artilharia = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Artilharia')
lista_jogadores = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogadores')
lista_estadios = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Estádios')
lista_observacoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Observações')
lista_colocacoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Posições')
lista_competicoes = pd.DataFrame(
    columns=['codigo', 'competicao'],
    data = ([
        ['ne', 'Copa do Nordeste'],
        ['br1', 'Campeonato Brasileiro Série A1']
    ]))

#funções
def partidas(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, clube = 0):

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

    #
    jogos = jogos[jogos['Competição'] == competicao] if competicao != 0 else jogos
    jogos = jogos[jogos['Ano'] == ano] if ano != 0 else jogos    
    jogos = jogos[jogos['Grupo'] == grupo] if grupo != 0 else jogos
    jogos = jogos[jogos['Fase'] == fase] if fase != 0 else jogos
    jogos = jogos[jogos['ID'].str.contains(clube)] if clube != 0 else jogos
    jogos = jogos[jogos['Rodada'] == rodada] if rodada != 0 else jogos
    #jogos = jogos.sort_values(['Data'], ascending = [False]) if clube != 0 else jogos.sort_values(['Data'], ascending = [True])

    return pd.merge(left=jogos, right=lista_estadios, left_on='Local', right_on='estadio', how='left').drop(['completo', 'estadio', 'capacidade', 'cidade', 'estado', 'data_inauguracao', 'partida_inauguracao'], axis=1)

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

    #
    classificacao = classificacao[classificacao['Competição'] == competicao] if competicao != 0 else classificacao
    classificacao = classificacao[classificacao['Ano'] == ano] if ano != 0 else classificacao
    classificacao = classificacao[classificacao['Grupo'] == grupo] if grupo != 0 else classificacao
    classificacao = classificacao[classificacao['Fase'] == fase] if fase != 0 else classificacao
    classificacao = classificacao[classificacao['Clube'].str.contains(clube)] if clube != 0 else classificacao
    classificacao = classificacao.sort_values(['Pts', 'Saldo'], ascending = [False, False])
    classificacao = classificacao.groupby(['Clube']).sum().reset_index().sort_values(['Pts', 'V', 'Saldo', 'GP'], ascending = [False, False, False, False]).drop(columns=['Ano']).reset_index().drop('index', axis=1)
    classificacao.insert(0, 'Pos', classificacao.index + 1)
    return pd.merge(left=classificacao, right=lista_clubes, left_on='Clube', right_on='clube', how='left').drop(['completo', 'clube', 'fundacao', 'cidade', 'estado'], axis=1)

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

def mata_mata(competicao = 0, ano = 0, grupo = 0, fase = 0, clube = 0):
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
        'Obs': jogos['obs'],
        'Confronto1': jogos['confronto1'],
        'Confronto2': jogos['confronto2'],
        'Gol_M': jogos['gol_m'],
        'Gol_V': jogos['gol_v'],
    })

    jogos = jogos.where(pd.notnull(jogos), '')

    jogos = pd.merge(left=jogos, right=lista_estadios, left_on='Local', right_on='estadio', how='left').drop(['completo', 'estadio', 'capacidade', 'cidade', 'estado', 'data_inauguracao', 'partida_inauguracao'], axis=1)

    #
    jogos = jogos[jogos['Competição'] == competicao] if competicao != 0 else jogos
    jogos = jogos[jogos['Ano'] == ano] if ano != 0 else jogos    
    jogos = jogos[jogos['Grupo'] == grupo] if grupo != 0 else jogos
    jogos = jogos[jogos['Fase'] == fase] if fase != 0 else jogos
    jogos = jogos[jogos['ID'].str.contains(clube)] if clube != 0 else jogos
    jogos = jogos.sort_values(['Data'], ascending = [False]) if clube != 0 else jogos.sort_values(['Data'], ascending = [True])

    mata_mata = pd.merge(left = jogos, right = jogos, left_on='Confronto1', right_on='Confronto2')
    mata_mata = mata_mata[mata_mata['Rodada_x'] == 'Ida']

    mata_mata2 = pd.DataFrame({
        'ID_Ida': mata_mata['ID_x'],
        'Competição_Ida': mata_mata['Competição_x'],
        'Ano_Ida': mata_mata['Ano_x'],
        'Data_Ida': mata_mata['Data_x'],
        'Horário_Ida': mata_mata['Horário_x'],
        'Grupo_Ida': mata_mata['Grupo_x'],
        'Fase_Ida': mata_mata['Fase_x'],
        'Rodada_Ida': mata_mata['Rodada_x'],
        'Mandante_Ida': mata_mata['Mandante_x'],
        'Placar_Ida': mata_mata['Placar_x'],
        'Visitante_Ida': mata_mata['Visitante_x'],
        'Local_Ida': mata_mata['Local_x'],
        'Slug_Local_Ida': mata_mata['slug_x'],
        'Obs_Ida': mata_mata['Obs_x'],
        'Confronto1_Ida': mata_mata['Confronto1_x'],
        'Confronto2_Ida': mata_mata['Confronto2_x'],
        'ID_Volta': mata_mata['ID_y'],
        'Competição_Volta': mata_mata['Competição_y'],
        'Ano_Volta': mata_mata['Ano_y'],
        'Data_Volta': mata_mata['Data_y'],
        'Horário_Volta': mata_mata['Horário_y'],
        'Grupo_Volta': mata_mata['Grupo_y'],
        'Fase_Volta': mata_mata['Fase_y'],
        'Rodada_Volta': mata_mata['Rodada_y'],
        'Mandante_Volta': mata_mata['Mandante_y'],
        'Placar_Volta': mata_mata['Placar_y'],
        'Visitante_Volta': mata_mata['Visitante_y'],
        'Local_Volta': mata_mata['Local_y'],
        'Slug_Local_Volta': mata_mata['slug_y'],
        'Obs_Volta': mata_mata['Obs_y'],
        'Confronto1_Volta': mata_mata['Confronto1_y'],
        'Confronto2_Volta': mata_mata['Confronto2_y'],
        'Gol_M_Ida': mata_mata['Gol_M_x'],
        'Gol_M_Volta': mata_mata['Gol_M_y'],
        'Gol_V_Ida': mata_mata['Gol_V_x'],
        'Gol_V_Volta': mata_mata['Gol_V_y'],
        'Gol_M_IDA': mata_mata['Gol_M_x'] + mata_mata['Gol_V_y'],
        'Gol_V_IDA': mata_mata['Gol_V_x'] + mata_mata['Gol_M_y']
    })

    return mata_mata2

def colocacao(competicao, ano, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1):
    lista_colocacoes2 = lista_colocacoes[lista_colocacoes['competicao'] == competicao]
    lista_colocacoes2 = lista_colocacoes2[lista_colocacoes2['ano'] == ano]

    cla = classificacao(competicao, ano = ano, grupo = 0, fase = 0, vitoria = vitoria, empate_sem_gols = empate_sem_gols, empate_com_gols = empate_com_gols, clube = 0)
    cla['Aproveitamento'] = round(cla['Pts'] / (cla['J']*3)*100, 2)

    pos = pd.merge(left = lista_colocacoes2, right = cla, left_on='clube', right_on = 'Clube')
    return pos.drop(['clube', 'Pos'], axis = 1)

def grupos_cruzados(competicao, ano, fase, grupo):
    lista_gruposcruzados = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Grupos Cruzados')
    grupos = pd.merge(left=lista_gruposcruzados, right=classificacao(competicao = 0, ano = ano, grupo = 0, fase = fase, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0), left_on='clube', right_on='Clube')
    grupos = grupos[grupos['competicao'] == competicao]
    grupos = grupos[grupos['ano'] == ano]
    grupos = grupos[grupos['grupo'] == grupo]
    grupos = grupos.drop('Pos', axis=1)
    grupos = grupos.rename(columns={'competicao': 'Competição', 'ano': 'Ano', 'grupo': 'Grupo', 'clube': 'Clube', 'pos': 'Pos'})
    return grupos.sort_values('Pos')

def segundos_colocados(competicao, ano, fase):
    lista_sugundoscolocados = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Segundos Colocados')
    lista_sugundoscolocados = lista_sugundoscolocados[lista_sugundoscolocados['competicao'] == competicao]
    lista_sugundoscolocados = lista_sugundoscolocados[lista_sugundoscolocados['ano'] == ano]

    grupos = lista_jogos[lista_jogos['fase'] == fase]
    grupos = grupos[grupos['ano'] == ano]
    grupos = grupos[['mandante', 'grupo']].drop_duplicates(subset=['mandante'])

    classf = classificacao(competicao = competicao, ano = ano, grupo = 0, fase = fase, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0)
    segundos = pd.merge(left=lista_sugundoscolocados, right=classf, left_on='clube', right_on='Clube').drop(['Pos'], axis=1)    
    segundos = pd.merge(left=segundos, right=grupos, left_on='Clube', right_on='mandante')
    segundos = segundos.rename(columns={'pos': 'Pos', 'grupo': 'Grupo'})
    segundos['Grupo'] = segundos['Grupo'].apply(lambda x: x.replace('Grupo ', ''))
    return segundos

def n_participacoes(competicao, clube):
    participacoes = lista_jogos[lista_jogos['competicao'] == competicao]
    participacoes = participacoes[participacoes['mandante'] == clube][['ano', 'mandante']].drop_duplicates().shape[0]
    return participacoes

def n_titulos(competicao, clube):
    n__titulos = lista_campeoes[lista_campeoes['competicao'] == competicao]
    n__titulos = n__titulos[n__titulos['clube'] == clube].shape[0]
    return n__titulos

def n_titulos_edicoes(competicao, clube):
    n__titulos = lista_campeoes[lista_campeoes['competicao'] == competicao]
    n__titulos = n__titulos[n__titulos['clube'] == clube]
    return n__titulos




#flask app
app = Flask(__name__)

## competições (copa do nordeste)
@app.route('/')
@app.route('/competicoes/')
#@app.route('/competicoes/ne/')
@app.route('/clubes/')
def index():  
    return render_template('home.html',
        title = 'NE Dados FC',
        lista_clubes = lista_clubes.to_dict('records'),
    )

@app.route('/competicoes/<sigla_competicao>')
@app.route('/competicoes/<sigla_competicao>/')
def comp(sigla_competicao):

    # parâmetros
    competicao = lista_competicoes[lista_competicoes['codigo'] == sigla_competicao]['competicao'][0]

    return render_template('/comp.html',

        title = competicao,

        # dados
        classificacao_geral = classificacao(competicao, ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0).to_dict('records'),
    )

## competições
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
        url = sigla_competicao,

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
        classificacao_final = colocacao(competicao, ano, vitoria = pts_vitoria,
            empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        # fase preliminar (pré)
        pre1=partidas(competicao, ano, 0, 'Primeira fase (Pré)', 'Único').to_dict('records'),
        pre1_2=mata_mata(competicao, ano, fase='Primeira fase (Pré)').to_dict('records'),
        pre2=partidas(competicao, ano, 0, 'Segunda fase (Pré)', 'Único').to_dict('records'),
        pre2_2=mata_mata(competicao, ano, fase='Segunda fase (Pré)').to_dict('records'),
        pre3=partidas(competicao, ano, 0, 'Terceira fase (Pré)', 'Único').to_dict('records'),
        pre3_2=mata_mata(competicao, ano, fase='Terceira fase (Pré)').to_dict('records'),

        # fase preliminar
        fase_preliminar_jogos = partidas(competicao, ano, 'Único', 'Fase preliminar').to_dict('records'),
        fase_preliminar_jogos2 = mata_mata(competicao, ano, fase='Fase preliminar (Pré)').to_dict('records'),

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

        grupos_cruzados_jogos = partidas(competicao, ano, 0, 'Primeira fase').to_dict('records'),
        grupo_a_cruzado_classificacao = grupos_cruzados(competicao, ano, fase = 'Primeira fase', grupo = 'A').to_dict('records'),
        grupo_b_cruzado_classificacao = grupos_cruzados(competicao, ano, fase = 'Primeira fase', grupo = 'B').to_dict('records'),

        segundoscolocados = segundos_colocados(competicao, ano, 'Primeira fase').to_dict('records'),

        # segunda fase / mata-matas
        grupo_e2_jogos = partidas(competicao, ano, 'Grupo E', 'Segunda fase').to_dict('records'),
        grupo_e2_classificacao = classificacao(
            competicao, ano, 'Grupo E', 'Segunda fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),
        
        grupo_f2_jogos = partidas(competicao, ano, 'Grupo F', 'Segunda fase').to_dict('records'),
        grupo_f2_classificacao = classificacao(
            competicao, ano, 'Grupo F', 'Segunda fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

        of=partidas(competicao, ano, 0, 'Oitavas de final', 'Único').to_dict('records'),
        of2=mata_mata(competicao, ano, fase='Oitavas de final').to_dict('records'),

        qf=partidas(competicao, ano, 0, 'Quartas de final', 'Único').to_dict('records'),
        qf2=mata_mata(competicao, ano, fase='Quartas de final').to_dict('records'),

        sf=partidas(competicao, ano, 0, 'Semifinal', 'Único').to_dict('records'),
        sf2=mata_mata(competicao, ano, fase='Semifinal').to_dict('records'),

        final=partidas(competicao, ano, 0, 'Final', 'Único').to_dict('records'),
        final2=mata_mata(competicao, ano, fase='Final').to_dict('records')
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

    return render_template('/clube.html',
        slug = slug,
        clube = nome_completo,
        nome_curto = nome_curto,
        escudo = escudo,
        fundacao = fundacao,
        cidade = cidade,
        estado = estado,
        geral = classificacao(competicao = 0, ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = nome_curto).to_dict('records'),
        copa_ne = classificacao(competicao = 'Copa do Nordeste', ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = nome_curto).to_dict('records'),
        ne_titulos = n_titulos('Copa do Nordeste', nome_curto),
        ne_titulos_edicoes = n_titulos_edicoes('Copa do Nordeste', nome_curto).to_dict('records'),
        ne_part = n_participacoes('Copa do Nordeste', nome_curto),
    )

## estádio
@app.route('/estadios/<estadio>')
def estadios(estadio):
    slug = lista_estadios[lista_estadios['slug'] == estadio].to_dict('records')[0]['slug']
    completo = lista_estadios[lista_estadios['slug'] == estadio].to_dict('records')[0]['completo']
    capacidade = lista_estadios[lista_estadios['slug'] == estadio].to_dict('records')[0]['capacidade']
    cidade = lista_estadios[lista_estadios['slug'] == estadio].to_dict('records')[0]['cidade']
    estado = lista_estadios[lista_estadios['slug'] == estadio].to_dict('records')[0]['estado']

    jogo_inauguracao = lista_estadios[lista_estadios['slug'] == estadio].to_dict('records')[0]['partida_inauguracao']
    jogo_inauguracao2 = partidas(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, clube = 0)

    return render_template('/estadios.html',
        title = completo,
        foto = slug,
        nome_completo = completo,
        capacidade = int(capacidade),
        cidade = cidade,
        estado = estado,
        jogo_inauguracao = jogo_inauguracao2[jogo_inauguracao2['ID'] == jogo_inauguracao].to_dict('records'),
    )

if __name__ == '__main__':
    app.run(debug=True) #debug=True, port=8080