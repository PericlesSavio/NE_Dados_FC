from flask import Flask, render_template
import pandas as pd

#dados
lista_jogos = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogos')
lista_jogos['data'] = pd.to_datetime(lista_jogos['data']).dt.date
lista_clubes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Clubes')
lista_campeoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Campeões')
#lista_artilharia = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Artilharia')
lista_jogadores = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Jogadores')
lista_gols = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Artilharia')
lista_estadios = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Estádios')
lista_observacoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Observações')
lista_colocacoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Posições')
lista_mundanca_clube = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Mudanças')
lista_competicoes = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Competições')


#funções
def partidas_1(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, id_jogo = 0):
    partidas = pd.merge(left=lista_jogos, right=lista_estadios, left_on='local', right_on='estadio', how='left')
    partidas = partidas.drop(['completo', 'estadio', 'capacidade', 'cidade', 'estado', 'data_inauguracao', 'partida_inauguracao'], axis=1)

    #parâmetros
    partidas = partidas[partidas['competicao'] == competicao] if competicao != 0 else partidas
    partidas = partidas[partidas['ano'] == ano] if ano != 0 else partidas    
    partidas = partidas[partidas['grupo'] == grupo] if grupo != 0 else partidas
    partidas = partidas[partidas['fase'] == fase] if fase != 0 else partidas
    partidas = partidas[partidas['id_jogo'].str.contains(id_jogo)] if id_jogo != 0 else partidas
    partidas = partidas[partidas['rodada'] == rodada] if rodada != 0 else partidas    

    partidas = pd.merge(left=partidas, right=lista_clubes, left_on='mandante', right_on='clube', how='left')
    partidas = partidas.drop(['completo', 'clube', 'fundacao', 'cidade', 'estado'], axis=1)

    partidas = pd.merge(left=partidas, right=lista_clubes, left_on='visitante', right_on='clube', how='left')
    partidas = partidas.drop(['completo', 'clube', 'fundacao', 'cidade', 'estado'], axis=1)

    partidas = partidas.rename(columns={"slug_clube_x": "slug_clube_m", "slug_clube_y": "slug_clube_v"})

    partidas = partidas.where(pd.notnull(partidas), '')
    
    return partidas

def classificacao(competicao = 0, ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0):
    clasf1 = pd.DataFrame({
        'id_jogo': lista_jogos['id_jogo'],
        'ano': lista_jogos['ano'],
        'competicao': lista_jogos['competicao'],
        'grupo': lista_jogos['grupo'],
        'fase': lista_jogos['fase'],
        'estadio': lista_jogos['local'],
        'clube': lista_jogos['mandante'],
        'pts': 0,
        'j': 1,
        'v': 0,
        'e': 0,
        'd': 0,
        'gp': lista_jogos['gol_m'],
        'gc': lista_jogos['gol_v'],
        'saldo': lista_jogos['gol_m'] - lista_jogos['gol_v'],
    })
    clasf2 = pd.DataFrame({
        'id_jogo': lista_jogos['id_jogo'],
        'ano': lista_jogos['ano'],
        'competicao': lista_jogos['competicao'],
        'grupo': lista_jogos['grupo'],
        'fase': lista_jogos['fase'],
        'estadio': lista_jogos['local'],
        'clube': lista_jogos['visitante'],
        'pts': 0,
        'j': 1,
        'v': 0,
        'e': 0,
        'd': 0,
        'gp': lista_jogos['gol_v'],
        'gc': lista_jogos['gol_m'],
        'saldo': lista_jogos['gol_v'] - lista_jogos['gol_m'],
    })   

    classificacao = pd.concat([clasf1, clasf2])
    
    classificacao.loc[classificacao['gp'] > classificacao['gc'], 'v'] = 1
    classificacao.loc[classificacao['gp'] == classificacao['gc'], 'e'] = 1
    classificacao.loc[classificacao['gp'] < classificacao['gc'], 'd'] = 1
    classificacao.loc[classificacao['gp'] > classificacao['gc'], 'pts'] = vitoria
    classificacao.loc[(classificacao['gp'] == classificacao['gc']) & (classificacao['gp'] + classificacao['gc'] == 0), 'pts'] = empate_sem_gols
    classificacao.loc[(classificacao['gp'] == classificacao['gc']) & (classificacao['gp'] + classificacao['gc'] > 0), 'pts'] = empate_com_gols
    classificacao.loc[classificacao['gp'] < classificacao['gc'], 'pts'] = 0

    #
    classificacao = classificacao[classificacao['competicao'] == competicao] if competicao != 0 else classificacao
    classificacao = classificacao[classificacao['ano'] == ano] if ano != 0 else classificacao
    classificacao = classificacao[classificacao['grupo'] == grupo] if grupo != 0 else classificacao
    classificacao = classificacao[classificacao['fase'] == fase] if fase != 0 else classificacao
    classificacao = classificacao[classificacao['clube'].str.contains(clube)] if clube != 0 else classificacao
    classificacao = classificacao.sort_values(['pts', 'saldo'], ascending = [False, False])
    classificacao = classificacao.groupby(['clube']).sum().reset_index().sort_values(['pts', 'v', 'saldo', 'gp'], ascending = [False, False, False, False]).drop(columns=['ano']).reset_index().drop('index', axis=1)
    classificacao.insert(0, 'pos', classificacao.index + 1)
    return pd.merge(left=classificacao, right=lista_clubes, left_on='clube', right_on='clube', how='left').drop(['completo', 'fundacao', 'cidade', 'estado'], axis=1)

def participacoes(ano, competicao):
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
        'Slug': participacoes['slug_clube'],
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
    return pd.merge(left=clube_campeao, right=lista_clubes, left_on='clube', right_on='clube')[['clube', 'completo', 'titulos', 'slug_clube']]

def artilharia(competicao = 0, ano = 0):
    artilharia = pd.merge(left = lista_gols, right = lista_jogos, left_on='id_jogo', right_on='id_jogo')
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
        'Nº de partidas': classificacao('Copa do Nordeste', ano).sum()['j'],
        'Total de gols': classificacao('Copa do Nordeste', ano).sum()['gp'],
        'Média de gols': "{:.2f}".format(classificacao('Copa do Nordeste', ano).sum()['gp'] / classificacao('Copa do Nordeste', ano).sum()['j']),
        'Período': [inicio, final]
        }
    return dados

def clube_info(clube):
    clube2 = lista_clubes[lista_clubes['slug_clube'] == clube]
    return clube2

def partida_dados(id):
    partida = lista_jogos[lista_jogos['id_jogo'] == id]
    return partida

def mata_mata(competicao = 0, ano = 0, grupo = 0, fase = 0, clube = 0):
    jogos = pd.merge(left = lista_jogos, right = lista_observacoes, left_on='id_jogo', right_on='id_jogo', how='left')

    jogos = pd.DataFrame({
        'id': jogos['id_jogo'],
        'competição': jogos['competicao'],
        'ano': jogos['ano'],
        'data': jogos['data'],
        'horário': jogos['horario'],
        'grupo': jogos['grupo'],
        'fase': jogos['fase'],
        'rodada': jogos['rodada'],
        'mandante': jogos['mandante'],
        'placar': jogos['gol_m'].astype(str) + '-' + jogos['gol_v'].astype(str),
        'visitante': jogos['visitante'],
        'local': jogos['local'],
        'obs': jogos['obs'],
        'confronto1': jogos['confronto1'],
        'confronto2': jogos['confronto2'],
        'gol_m': jogos['gol_m'],
        'gol_v': jogos['gol_v'],
    })

    jogos = jogos.where(pd.notnull(jogos), '')

    jogos = pd.merge(left=jogos, right=lista_estadios, left_on='local', right_on='estadio', how='left').drop(['completo', 'estadio', 'capacidade', 'cidade', 'estado', 'data_inauguracao', 'partida_inauguracao'], axis=1)

    #
    jogos = jogos[jogos['competição'] == competicao] if competicao != 0 else jogos
    jogos = jogos[jogos['ano'] == ano] if ano != 0 else jogos    
    jogos = jogos[jogos['grupo'] == grupo] if grupo != 0 else jogos
    jogos = jogos[jogos['fase'] == fase] if fase != 0 else jogos
    jogos = jogos[jogos['id'].str.contains(clube)] if clube != 0 else jogos
    jogos = jogos.sort_values(['data'], ascending = [False]) if clube != 0 else jogos.sort_values(['data'], ascending = [True])

    mata_mata = pd.merge(left = jogos, right = jogos, left_on='confronto1', right_on='confronto2')
    mata_mata = mata_mata[mata_mata['rodada_x'] == 'Ida']

    mata_mata2 = pd.DataFrame({
        'id_ida': mata_mata['id_x'],
        'competição_ida': mata_mata['competição_x'],
        'ano_ida': mata_mata['ano_x'],
        'data_ida': mata_mata['data_x'],
        'horário_ida': mata_mata['horário_x'],
        'grupo_ida': mata_mata['grupo_x'],
        'fase_ida': mata_mata['fase_x'],
        'rodada_ida': mata_mata['rodada_x'],
        'mandante_ida': mata_mata['mandante_x'],
        'placar_ida': mata_mata['placar_x'],
        'visitante_ida': mata_mata['visitante_x'],
        'local_ida': mata_mata['local_x'],
        'slug_local_ida': mata_mata['slug_estadio_x'],
        'obs_ida': mata_mata['obs_x'],
        'confronto1_ida': mata_mata['confronto1_x'],
        'confronto2_ida': mata_mata['confronto2_x'],
        'id_volta': mata_mata['id_y'],
        'competição_volta': mata_mata['competição_y'],
        'ano_volta': mata_mata['ano_y'],
        'data_volta': mata_mata['data_y'],
        'horário_volta': mata_mata['horário_y'],
        'grupo_volta': mata_mata['grupo_y'],
        'fase_volta': mata_mata['fase_y'],
        'rodada_volta': mata_mata['rodada_y'],
        'mandante_volta': mata_mata['mandante_y'],
        'placar_volta': mata_mata['placar_y'],
        'visitante_volta': mata_mata['visitante_y'],
        'local_volta': mata_mata['local_y'],
        'slug_local_volta': mata_mata['slug_estadio_y'],
        'obs_volta': mata_mata['obs_y'],
        'confronto1_volta': mata_mata['confronto1_y'],
        'confronto2_volta': mata_mata['confronto2_y'],
        'gol_m_ida': mata_mata['gol_m_x'],
        'gol_m_volta': mata_mata['gol_m_y'],
        'gol_v_ida': mata_mata['gol_v_x'],
        'gol_v_volta': mata_mata['gol_v_y'],
        'gol_m_ida': mata_mata['gol_m_x'] + mata_mata['gol_v_y'],
        'gol_v_ida': mata_mata['gol_v_x'] + mata_mata['gol_m_y']
    })

    return mata_mata2

def colocacao(competicao, ano, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1):
    lista_colocacoes2 = lista_colocacoes[lista_colocacoes['competicao'] == competicao]
    lista_colocacoes2 = lista_colocacoes2[lista_colocacoes2['ano'] == ano]

    cla = classificacao(competicao, ano = ano, grupo = 0, fase = 0, vitoria = vitoria, empate_sem_gols = empate_sem_gols, empate_com_gols = empate_com_gols, clube = 0)
    cla['aproveitamento'] = round(cla['pts'] / (cla['j']*3)*100, 2)
    cla = cla.drop(['pos'], axis = 1)
    pos = pd.merge(left = lista_colocacoes2, right = cla, left_on='clube', right_on = 'clube')

    return pos

def grupos_cruzados(competicao, ano, fase, grupo):
    lista_gruposcruzados = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Grupos Cruzados')
    grupos = pd.merge(left=lista_gruposcruzados, right=classificacao(competicao = 0, ano = ano, grupo = 0, fase = fase, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0), left_on='clube', right_on='clube')
    grupos = grupos[grupos['competicao'] == competicao]
    grupos = grupos[grupos['ano'] == ano]
    grupos = grupos[grupos['grupo'] == grupo]
    grupos = grupos.drop('pos_y', axis=1)
    grupos = grupos.rename(columns={'pos_x': 'pos'})
    return grupos.sort_values('pos')

def segundos_colocados(competicao, ano, fase):
    lista_sugundoscolocados = pd.read_excel('dados/Futebol Nordestino.xlsx', sheet_name='Segundos Colocados')
    lista_sugundoscolocados = lista_sugundoscolocados[lista_sugundoscolocados['competicao'] == competicao]
    lista_sugundoscolocados = lista_sugundoscolocados[lista_sugundoscolocados['ano'] == ano]

    grupos = lista_jogos[lista_jogos['fase'] == fase]
    grupos = grupos[grupos['ano'] == ano]
    grupos = grupos[['mandante', 'grupo']].drop_duplicates(subset=['mandante'])

    classf = classificacao(competicao = competicao, ano = ano, grupo = 0, fase = fase, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0).drop(['pos'], axis=1) 
    segundos = pd.merge(left=lista_sugundoscolocados, right=classf, left_on='clube', right_on='clube')
    segundos = pd.merge(left=segundos, right=grupos, left_on='clube', right_on='mandante')
    #segundos = segundos.rename(columns={'pos': 'Pos', 'grupo': 'Grupo'})
    segundos['grupo'] = segundos['grupo'].apply(lambda x: x.replace('Grupo ', ''))
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

def gols_partida(id_jogo):
    gols = lista_gols[lista_gols['id_jogo'] == id_jogo]
    gols = pd.merge(left=gols, right=lista_jogadores, left_on='jogador', right_on='jogador', how='left')
    gols = pd.merge(left=gols, right=lista_jogos, left_on='id_jogo', right_on='id_jogo', how='left')
    gols = gols[['id_jogo', 'jogador', 'clube', 'tempo', 'min', 'tipo', 'alcunha', 'slug_jogador', 'mandante', 'visitante', 'gol_m', 'gol_v']]

    gols = pd.merge(left=gols, right=lista_clubes, left_on='clube', right_on='clube', how='left')

    gols.loc[(gols['clube'] == gols['mandante']) & (gols['tipo'] == 'Gol'), 'jogador_m'] = gols['alcunha']
    gols.loc[(gols['clube'] == gols['visitante']) & (gols['tipo'] == 'Gol'), 'jogador_v'] = gols['alcunha']

    gols.loc[(gols['clube'] == gols['mandante']) & (gols['tipo'] == 'Contra'), 'jogador_v'] = gols['alcunha']
    gols.loc[(gols['clube'] == gols['visitante']) & (gols['tipo'] == 'Contra'), 'jogador_m'] = gols['alcunha']

    #gols.loc[(gols['clube'] == gols['mandante']) & (gols['tipo'] == 'Gol'), 'gol_tipo_m'] = 'Gol'
    #gols.loc[(gols['clube'] == gols['visitante']) & (gols['tipo'] == 'Gol'), 'gol_tipo_v'] = 'Gol'

    try:
        gols.loc[(gols['clube'] == gols['mandante']) & (gols['tipo'] == 'Contra'), 'gol_tipo_v'] = 'Contra'
    except:
        pass
    
    try:
        gols.loc[(gols['clube'] == gols['visitante']) & (gols['tipo'] == 'Contra'), 'gol_tipo_m'] = 'Contra'
    except:
        pass

    try:
        gols[['id_jogo', 'jogador', 'clube', 'tempo', 'min', 'tipo', 'alcunha',
       'slug_jogador', 'mandante', 'visitante', 'gol_m', 'gol_v', 'slug_clube', 'jogador_m', 'jogador_v',
       'gol_tipo_v', 'gol_tipo_m']]
    except:
        pass   

    return gols.where(pd.notnull(gols), '')

#flask app
app = Flask(__name__)

## competições (copa do nordeste)

@app.route('/teste')
@app.route('/competicoes/')
#@app.route('/competicoes/ne/')
@app.route('/clubes/')
@app.route('/')
def index():  
    return render_template('home.html',
        title = 'NE Dados FC',
        lista_clubes = lista_clubes.to_dict('records'),
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
    
    competicao = lista_competicoes[lista_competicoes['codigo'] == sigla_competicao]['competicao'].reset_index(drop=True)[0]    
    try:
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
            pre1=partidas_1(competicao, ano, 0, 'Primeira fase (Pré)', 'Único').to_dict('records'),
            pre1_2=mata_mata(competicao, ano, fase='Primeira fase (Pré)').to_dict('records'),
            pre2=partidas_1(competicao, ano, 0, 'Segunda fase (Pré)', 'Único').to_dict('records'),
            pre2_2=mata_mata(competicao, ano, fase='Segunda fase (Pré)').to_dict('records'),
            pre3=partidas_1(competicao, ano, 0, 'Terceira fase (Pré)', 'Único').to_dict('records'),
            pre3_2=mata_mata(competicao, ano, fase='Terceira fase (Pré)').to_dict('records'),

            # fase preliminar
            fase_preliminar_jogos = partidas_1(competicao, ano, 'Único', 'Fase preliminar').to_dict('records'),
            fase_preliminar_jogos2 = mata_mata(competicao, ano, fase='Fase preliminar (Pré)').to_dict('records'),

            # primeira fase
            primeira_fase_jogos = partidas_1(competicao, ano, 'Único', 'Primeira fase').to_dict('records'),
            primeira_fase_classificacao = classificacao(
                competicao, ano, 'Único', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            grupo_a_jogos = partidas_1(competicao, ano, 'Grupo A', 'Primeira fase').to_dict('records'),
            grupo_a_classificacao = classificacao(
                competicao, ano, 'Grupo A', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            grupo_b_jogos = partidas_1(competicao, ano, 'Grupo B', 'Primeira fase').to_dict('records'),
            grupo_b_classificacao = classificacao(
                competicao, ano, 'Grupo B', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),   
            
            grupo_c_jogos = partidas_1(competicao, ano, 'Grupo C', 'Primeira fase').to_dict('records'),
            grupo_c_classificacao = classificacao(
                competicao, ano, 'Grupo C', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            grupo_d_jogos = partidas_1(competicao, ano, 'Grupo D', 'Primeira fase').to_dict('records'),
            grupo_d_classificacao = classificacao(
                competicao, ano, 'Grupo D', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            grupo_e_jogos = partidas_1(competicao, ano, 'Grupo E', 'Primeira fase').to_dict('records'),
            grupo_e_classificacao = classificacao(
                competicao, ano, 'Grupo E', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            grupo_f_jogos = partidas_1(competicao, ano, 'Grupo F', 'Primeira fase').to_dict('records'),
            grupo_f_classificacao = classificacao(
                competicao, ano, 'Grupo F', 'Primeira fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            grupos_cruzados_jogos = partidas_1(competicao, ano, 0, 'Primeira fase').to_dict('records'),
            grupo_a_cruzado_classificacao = grupos_cruzados(competicao, ano, fase = 'Primeira fase', grupo = 'A').to_dict('records'),
            grupo_b_cruzado_classificacao = grupos_cruzados(competicao, ano, fase = 'Primeira fase', grupo = 'B').to_dict('records'),

            segundoscolocados = segundos_colocados(competicao, ano, 'Primeira fase').to_dict('records'),

            # segunda fase / mata-matas
            grupo_e2_jogos = partidas_1(competicao, ano, 'Grupo E', 'Segunda fase').to_dict('records'),
            grupo_e2_classificacao = classificacao(
                competicao, ano, 'Grupo E', 'Segunda fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),
            
            grupo_f2_jogos = partidas_1(competicao, ano, 'Grupo F', 'Segunda fase').to_dict('records'),
            grupo_f2_classificacao = classificacao(
                competicao, ano, 'Grupo F', 'Segunda fase', empate_sem_gols = pts_empate_sem_gols, empate_com_gols = pts_empate_com_gols).to_dict('records'),

            of=partidas_1(competicao, ano, 0, 'Oitavas de final', 'Único').to_dict('records'),
            of2=mata_mata(competicao, ano, fase='Oitavas de final').to_dict('records'),

            qf=partidas_1(competicao, ano, 0, 'Quartas de final', 'Único').to_dict('records'),
            qf2=mata_mata(competicao, ano, fase='Quartas de final').to_dict('records'),

            sf=partidas_1(competicao, ano, 0, 'Semifinal', 'Único').to_dict('records'),
            sf2=mata_mata(competicao, ano, fase='Semifinal').to_dict('records'),

            d3l=partidas_1(competicao, ano, 0, 'Decisão de 3º lugar', 'Único').to_dict('records'),

            final=partidas_1(competicao, ano, 0, 'Final', 'Único').to_dict('records'),
            final2=mata_mata(competicao, ano, fase='Final').to_dict('records')
        )
    except:
        return render_template('/404.html')


@app.route('/competicoes/<sigla_competicao>')
@app.route('/competicoes/<sigla_competicao>/')
def comp(sigla_competicao):

    # parâmetros
    competicao = lista_competicoes[lista_competicoes['codigo'] == sigla_competicao]['competicao'].reset_index(drop=True)[0]

    return render_template('/comp.html',

        title = competicao,

        # dados
        classificacao_geral = classificacao(competicao, ano = 0, grupo = 0, fase = 0, vitoria = 3, empate_sem_gols = 1, empate_com_gols = 1, clube = 0).to_dict('records'),
    )


## clubes
@app.route('/clubes/<clube>')
def clubes(clube):
    slug = clube_info(clube)['slug_clube'].iloc[0]
    nome_completo = clube_info(clube)['completo'].iloc[0]
    nome_curto = clube_info(clube)['clube'].iloc[0]
    escudo = clube_info(clube)['slug_clube'].iloc[0]
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
    slug = lista_estadios[lista_estadios['slug_estadio'] == estadio].to_dict('records')[0]['slug_estadio']
    completo = lista_estadios[lista_estadios['slug_estadio'] == estadio].to_dict('records')[0]['completo']
    capacidade = lista_estadios[lista_estadios['slug_estadio'] == estadio].to_dict('records')[0]['capacidade']
    cidade = lista_estadios[lista_estadios['slug_estadio'] == estadio].to_dict('records')[0]['cidade']
    estado = lista_estadios[lista_estadios['slug_estadio'] == estadio].to_dict('records')[0]['estado']

    jogo_inauguracao = lista_estadios[lista_estadios['slug_estadio'] == estadio].to_dict('records')[0]['partida_inauguracao']
    jogo_inauguracao2 = partidas_1(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, id_jogo = 0)

    return render_template('/estadios.html',
        title = completo,
        foto = slug,
        nome_completo = completo,
        capacidade = int(capacidade),
        cidade = cidade,
        estado = estado,
        jogo_inauguracao = jogo_inauguracao2[jogo_inauguracao2['id_jogo'] == jogo_inauguracao].to_dict('records'),
    )

## partidas
@app.route('/partidas/<partida>')
def partidas(partida):
    partida_dados = partidas_1(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, id_jogo = partida)

    try:
        slug_mandante = partida_dados.loc[0, 'slug_clube_m']
        slug_visitante = partida_dados.loc[0, 'slug_clube_v']
    
        return render_template('/partidas.html',
            title = partida_dados.loc[0, 'mandante'] + ' ' + str(partida_dados.loc[0, 'gol_m']) + '-' + str(partida_dados.loc[0, 'gol_v']) + ' ' + partida_dados.loc[0, 'visitante'],
            gols = gols_partida(partida).to_dict('records'),
            mandante = partida_dados.loc[0, 'mandante'],
            visitante = partida_dados.loc[0, 'visitante'],
            partida = partidas_1(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, id_jogo = partida).to_dict('records'),
            slug_mandante = slug_mandante,
            slug_visitante = slug_visitante,
            gol_m = partidas_1(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, id_jogo = partida).loc[0, 'gol_m'],
            gol_v = partidas_1(competicao = 0, ano = 0, grupo = 0, fase = 0, rodada = 0, id_jogo = partida).loc[0, 'gol_v'],
        )
    except:
        return render_template('/404.html')


@app.route('/jogador/<jogador>')
def jogador(jogador):
    
    jogador_dados = lista_jogadores[lista_jogadores['slug_jogador'] == jogador].reset_index()

    try:
        return render_template('/jogador.html',
            title = jogador_dados.loc[0, 'jogador'],
            alcunha = jogador_dados.loc[0, 'alcunha'],
        )
    except:
        #return render_template('/404.html')
        return render_template('/jogador.html',
            title = jogador_dados.loc[0, 'jogador'],
            alcunha = jogador_dados.loc[0, 'alcunha'],
        )



if __name__ == '__main__':
    app.run(debug=True) #debug=True, port=8080