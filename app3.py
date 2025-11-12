import dash
from dash import html, dcc, Input, Output, State, ctx
import pandas as pd
import io, base64
from PIL import Image, ImageDraw, ImageFont
import os

# Inicializa o app com meta viewport (responsivo)
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    index_string='''
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Estatísticas do Jogo</title>
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
)
server = app.server

# Estatísticas
grupo1 = ["Gols", "Finalizações", "Chutes no Gol", "Escanteios"]
grupo2 = ["Faltas", "Cartões", "Impedimentos"]

# DataFrames iniciais
dados_time_a = pd.DataFrame({"Estatística": grupo1 + grupo2, "Quantidade": [0]*len(grupo1 + grupo2)})
dados_time_b = pd.DataFrame({"Estatística": grupo1 + grupo2, "Quantidade": [0]*len(grupo1 + grupo2)})

# Layout principal
app.layout = html.Div(
    style={"padding": "10px", "maxWidth": "100vw", "overflowX": "hidden"},
    children=[
        html.H1("📊 Estatísticas do Jogo", style={"textAlign": "center"}),

        # Times
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "10px", "justifyContent": "center"},
            children=[
                html.Div(style={"flex": "1", "minWidth": "250px"}, children=[
                    html.Label("Time A (Esquerda):"),
                    dcc.Input(id="input-time-a", type="text", placeholder="Time A", value=" ")
                ]),
                html.Div(style={"flex": "1", "minWidth": "250px"}, children=[
                    html.Label("Time B (Direita):"),
                    dcc.Input(id="input-time-b", type="text", placeholder="Time B", value=" ")
                ]),
            ],
        ),

        # Botões
        html.Div(
            style={"display": "flex", "flexWrap": "wrap", "gap": "20px", "justifyContent": "center"},
            children=[
                html.Div(style={"flex": "1", "minWidth": "280px"}, children=[
                    html.H3("⚽ Time A", style={"textAlign": "center"}),
                    *[html.Button(
                        est,
                        id=f"a-{est}",
                        n_clicks=0,
                        style={
                            "background": "#007bff",
                            "color": "white",
                            "margin": "5px",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "width": "100%"
                        }
                    ) for est in grupo1 + grupo2]
                ]),
                html.Div(style={"flex": "1", "minWidth": "280px"}, children=[
                    html.H3("🏆 Time B", style={"textAlign": "center"}),
                    *[html.Button(
                        est,
                        id=f"b-{est}",
                        n_clicks=0,
                        style={
                            "background": "#dc3545",
                            "color": "white",
                            "margin": "5px",
                            "padding": "10px",
                            "borderRadius": "8px",
                            "width": "100%"
                        }
                    ) for est in grupo1 + grupo2]
                ]),
            ]
        ),

        html.H2("📈 Estatísticas Atuais", style={"marginTop": "30px", "textAlign": "center"}),

        html.Div(id="tabelas", style={"display": "flex", "justifyContent": "center", "gap": "20px", "flexWrap": "wrap"}),

        html.Div(
            html.Button(
                "📸 Gerar Imagens",
                id="btn-imagem",
                n_clicks=0,
                style={
                    "margin": "20px auto",
                    "background": "green",
                    "color": "white",
                    "padding": "10px 20px",
                    "borderRadius": "8px",
                    "display": "block"
                }
            ),
            style={"textAlign": "center"}
        ),

        # Imagens
        html.Div(
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "center",
                "alignItems": "center",
                "gap": "20px"
            },
            children=[
                html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                    html.H3("Imagem Grupo 1", style={"textAlign": "center"}),
                    html.Img(id="img-grupo1", style={
                        "width": "100%", "maxWidth": "100%", "height": "auto",
                        "display": "block", "margin": "0 auto", "borderRadius": "10px"
                    })
                ]),
                html.Div(style={"flex": "1", "minWidth": "300px"}, children=[
                    html.H3("Imagem Grupo 2", style={"textAlign": "center"}),
                    html.Img(id="img-grupo2", style={
                        "width": "100%", "maxWidth": "100%", "height": "auto",
                        "display": "block", "margin": "0 auto", "borderRadius": "10px"
                    })
                ])
            ]
        )
    ]
)

# ==========================
# Atualização de estatísticas
# ==========================
@app.callback(
    Output("tabelas", "children"),
    [Input(f"a-{est}", "n_clicks") for est in grupo1 + grupo2] +
    [Input(f"b-{est}", "n_clicks") for est in grupo1 + grupo2],
    [State("input-time-a", "value"), State("input-time-b", "value")]
)
def atualizar_dados(*args):
    global dados_time_a, dados_time_b
    time_a, time_b = args[-2], args[-1]

    if ctx.triggered_id:
        btn_id = ctx.triggered_id
        if btn_id.startswith("a-"):
            estat = btn_id[2:]
            dados_time_a.loc[dados_time_a["Estatística"] == estat, "Quantidade"] += 1
        elif btn_id.startswith("b-"):
            estat = btn_id[2:]
            dados_time_b.loc[dados_time_b["Estatística"] == estat, "Quantidade"] += 1

    tabela = html.Table([
        html.Thead(html.Tr([
            html.Th(time_a), html.Th("Estatística"), html.Th(time_b)
        ])),
        html.Tbody([
            html.Tr([
                html.Td(dados_time_a.loc[dados_time_a["Estatística"] == est, "Quantidade"].values[0]),
                html.Td(est),
                html.Td(dados_time_b.loc[dados_time_b["Estatística"] == est, "Quantidade"].values[0])
            ]) for est in grupo1 + grupo2
        ])
    ], style={"textAlign": "center", "border": "1px solid gray", "padding": "8px", "width": "100%", "maxWidth": "500px"})

    return [tabela]

# ==========================
# Geração de Imagem (ajustada)
# ==========================
def gerar_imagem_tabela(time_a, time_b, dados_a, dados_b, grupo):
    estatisticas = []
    for est in grupo:
        val_a = int(dados_a.loc[dados_a["Estatística"] == est, "Quantidade"].values[0])
        val_b = int(dados_b.loc[dados_b["Estatística"] == est, "Quantidade"].values[0])
        estatisticas.append((est, val_a, val_b))

    largura, altura = 1600, 900  # 📸 imagem bem maior e mais nítida
    cor_fundo = (10, 15, 20)
    cor_texto = (255, 255, 255)
    img = Image.new("RGB", (largura, altura), color=cor_fundo)
    draw = ImageDraw.Draw(img)

    try:
        fonte_titulo = ImageFont.truetype("arialbd.ttf", 70)
        fonte_texto = ImageFont.truetype("arial.ttf", 48)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()

    gols_a = int(dados_a.loc[dados_a["Estatística"] == "Gols", "Quantidade"].values[0])
    gols_b = int(dados_b.loc[dados_b["Estatística"] == "Gols", "Quantidade"].values[0])
    titulo = f"{time_a} [{gols_a}]  x  [{gols_b}] {time_b}"

    bbox_titulo = draw.textbbox((0, 0), titulo, font=fonte_titulo)
    w_titulo = bbox_titulo[2] - bbox_titulo[0]
    draw.text(((largura - w_titulo) // 2, 60), titulo, fill=cor_texto, font=fonte_titulo)

    # Cabeçalho
    x_coluna = [500, 800, 1100]
    cabecalho = [time_a, "Estatísticas", time_b]
    y_inicio = 200
    espacamento = 80

    for i, texto in enumerate(cabecalho):
        bbox = draw.textbbox((0, 0), texto, font=fonte_texto)
        w = bbox[2] - bbox[0]
        draw.text((x_coluna[i] - w // 2, y_inicio), texto, fill=cor_texto, font=fonte_texto)

    y = y_inicio + 100
    for est, val_a, val_b in estatisticas:
        draw.text((x_coluna[0], y), str(val_a), fill=cor_texto, font=fonte_texto, anchor="mm")
        draw.text((x_coluna[1], y), est, fill=cor_texto, font=fonte_texto, anchor="mm")
        draw.text((x_coluna[2], y), str(val_b), fill=cor_texto, font=fonte_texto, anchor="mm")
        y += espacamento

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return "data:image/png;base64," + base64.b64encode(buf.read()).decode()

# Callback imagem
@app.callback(
    [Output("img-grupo1", "src"), Output("img-grupo2", "src")],
    Input("btn-imagem", "n_clicks"),
    State("input-time-a", "value"),
    State("input-time-b", "value")
)
def gerar_imagens(n, time_a, time_b):
    if n == 0:
        return dash.no_update, dash.no_update
    img1 = gerar_imagem_tabela(time_a, time_b, dados_time_a, dados_time_b, grupo1)
    img2 = gerar_imagem_tabela(time_a, time_b, dados_time_a, dados_time_b, grupo2)
    return img1, img2

# Execução (Render)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=False)




