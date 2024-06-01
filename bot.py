import os
import numpy as np
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from graph_analysis import GraphAnalysis

admin_user_id = 'placeholder'
log_text = """                      
message: {}
user: {}, {}, {}
id: {} \n\n"""

welcome_message = 'Hi! Send me a list of edges to analyze the graph. Format: [(1,2),(2,3),...]'
error_message = "Error: հաստատ նայի ճիշտ ես գրել թե չէ, Սաքոյին խաբար արա, մեկ էլ եթե գրաֆդ կապակցված չի 5րդ հարցը կարա պռոբլեմ տա․ \n\n էսի էլ նավսյակի նայի կարողա օգնի, աշիբկի տեքստը-\n {}"


async def start(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    with open('logs.txt', 'a', encoding='utf-8') as file:
            file.write(log_text.format('started', user.first_name, user.last_name, user.username, user.id))
            
    await update.message.reply_text(welcome_message)


async def analyze_graph(update: Update, context: CallbackContext) -> None:
    edges_text = update.message.text.strip()
    user = update.message.from_user
    
    print('running...', user.first_name)
    with open('logs.txt', 'a', encoding='utf-8') as file:
            file.write(log_text.format(update.message.text.strip(), user.first_name, user.last_name, user.username, user.id))
            
    try:
        edges = eval(edges_text)
        n = max(max(e) for e in edges)
        adj_matrix = np.zeros((n, n), dtype=int)
        for (i, j) in edges:
            adj_matrix[i-1][j-1] = 1
            adj_matrix[j-1][i-1] = 1

        await update.message.reply_text('Հեսա սպասի մտածեմ․․․․')
        ga = GraphAnalysis(adj_matrix)
        graph_image = ga.draw_graph()

        max_indep_set = list(ga.maximum_independent_set())
        await update.message.reply_text(f'1)Ամենամեծ անկախ բազմությունը- {max_indep_set}')
        largest_matching = list(ga.largest_matching())
        await update.message.reply_text(f'2)Ամենամեծ զուգակցումը- {largest_matching}')
        min_vertex_cover = list(ga.minimum_vertex_cover())
        await update.message.reply_text(f'3)Ամենափոքր գագաթային ծածկույթը- {min_vertex_cover}')
        min_edge_cover = sorted(list(ga.min_edge_cover()), key=lambda x: x[0])
        await update.message.reply_text(f'4)Ամենափոքր կողային ծածկույթը- {min_edge_cover}')
        edges_to_remove = list(ga.edges_to_remove_for_eulerian_path())
        await update.message.reply_text(f'5)Նվազագույն քանակով կողերը Էյլերյանի համար- {edges_to_remove}')

        await update.message.reply_photo(photo=InputFile(graph_image, filename="graph.png"))
        result = (
            "մի հատ էլ իրար գլխի բերենք․\n\n"
            f"1) {max_indep_set}\n"
            f"2) {largest_matching}\n"
            f"3) {min_vertex_cover}\n"
            f"4) {min_edge_cover}\n"
            f"5) {edges_to_remove}\n"
        )

        await update.message.reply_text(result)
        await update.message.reply_text('եթե վատ ա նկարել գրաֆը կարաս նորից աշխատացնես, ուրիշ ձև կնկարի')

        
    except Exception as e:
        await update.message.reply_text(error_message.format(e))
        await context.bot.send_message(
            chat_id=admin_user_id, 
            text=f"Forwarded message from {user.first_name} - @{user.username}):\n\n{edges_text}\n\n" + str(e)
        )
    finally:
        print('finished...', user.first_name)


def main() -> None:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_graph))

    app.run_polling()

if __name__ == '__main__':
    main()
