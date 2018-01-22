from pytrivia import Category, Diffculty, Type, Trivia
my_api = Trivia(True)
response = my_api.request(1, Category.Books, Diffculty.Hard, Type.True_False)
results = response['results'][0]
question = results['question']

print(question)