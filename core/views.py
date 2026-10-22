from django.shortcuts import render

def dashboard(request):
    return render(request, 'core/dashboard.html')

def globe(request):
    return render(request, 'core/globe.html')

def predictions(request):
    return render(request, 'core/predictions.html')

def disasters(request):
    return render(request, 'core/disasters.html')

def simulator(request):
    return render(request, 'core/simulator.html')

def time_machine(request):
    return render(request, 'core/time_machine.html')

def carbon(request):
    return render(request, 'core/carbon.html')

def policy(request):
    return render(request, 'core/policy.html')

def reports(request):
    return render(request, 'core/reports.html')

def rankings(request):
    return render(request, 'core/rankings.html')

def chat(request):
    context = {
        'suggested_questions': [
            'What is global warming?',
            'How does CO2 affect climate?',
            'What causes sea level rise?',
            'How do floods form?',
            'What is the Paris Agreement?',
            'How does deforestation affect climate?',
            'What is my carbon footprint?',
            'How do cyclones form?',
            'What is Arctic amplification?',
            'How can renewable energy help?',
        ],
        'topics': [
            'Global Warming', 'CO2', 'Sea Level', 'Floods', 'Droughts',
            'Cyclones', 'Wildfires', 'Arctic', 'Renewables', 'Paris Agreement',
            'Deforestation', 'Carbon Footprint',
        ],
    }
    return render(request, 'core/chat.html', context)
