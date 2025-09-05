from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Country, State, City
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

# Create your views here.
def home(request):
    return render(request, "home.html")


# Country view 

def country_view(request):
    if request.method == 'POST':
        country = request.POST.get('country')
        Country.objects.create(name=country)
        return redirect('country')
        
    return render(request, 'country.html')

def get_country_details(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('q')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')
            if get_edit:
                country = get_object_or_404( Country, id = get_edit)
                context = {
                    'country':country
                }
                return render(request, 'country/country_edit_form.html', context)
            if get_delete:
                country = get_object_or_404( Country, id = get_delete)
                context={
                    'country':country
                }
                return render(request, 'country/country_delete_form.html', context)
            if search:
                countries = Country.objects.filter(
                     Q(name__icontains=search) 
                )
            else:
                countries = Country.objects.all().order_by('-id')
            
            page_num = request.GET.get('page')
            paginator = Paginator(countries,2)
            try:
                countries=paginator.page(page_num)
            except PageNotAnInteger:
                countries = paginator.page(1)
            except EmptyPage:
                countries = None
            
            return render(request, 'country/country_list.html', {'countries':countries} )
    
        except Exception as e:
            return HttpResponse(f'Error loading data: {str(e)}',e)
        
def edit_country(request, id):
    if request.method == 'POST':
        try:
            country = get_object_or_404(Country, id=id)
            country.name=request.POST.get('name')
            
            country.save()
            return redirect('country')
        except Exception as e:
            messages.error(request, f"Error updating country: {str(e)}")
            return redirect('country')

def delete_country(request, id):
    try:
        country = get_object_or_404(Country, id=id)

        if request.method == "POST":
            country.delete()   # ✅ fixed

            return redirect('country')

    except Exception as e:
        messages.error(request, f"Error deleting country: {str(e)}")
        return redirect('country')



# State view

def state_view(request):
    if request.method == "POST":
        country_id = request.POST.get("country")
        name = request.POST.get("name")
        if country_id and name:
            country = get_object_or_404(Country, id=country_id)
            State.objects.create(name=name, country=country)
        return redirect("state")
    return render(request, 'state.html')


def get_state_details(request):
    """HTMX load state list"""
    if request.headers.get('HX-Request'):
        
        try:
            search = request.GET.get('q')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')
            if get_edit:
                print("Edit is called",get_edit)
                state = get_object_or_404( State, id = get_edit)
                context = {
                    'state': state
                }
                return render(request, 'state/state_edit_form.html', context)
            if get_delete:
                state = get_object_or_404( State, id = get_delete)
                context={
                    'state': state
                }
                return render(request, 'state/state_delete_form.html', context)
            if search:
                states = State.objects.filter(
                     Q(name__icontains=search) 
                )
            else:
                states = State.objects.select_related("country").order_by("-created_at")
            
            page_num = request.GET.get('page')
            paginator = Paginator(states,2)
            try:
                states=paginator.page(page_num)
            except PageNotAnInteger:
                states = paginator.page(1)
            except EmptyPage:
                states = None
            
            return render(request, "state/state_list.html", {"states": states})
    
        except Exception as e:
            return HttpResponse(f'Error loading data: {str(e)}',e)
        

def edit_state(request, id):
    state = get_object_or_404(State, id=id)
    if request.method == "POST":
        country_id = request.POST.get("country")
        name = request.POST.get("name")
        if country_id and name:
            country = get_object_or_404(Country, id=country_id)
            state.country = country
            state.name = name
            state.save()
        return redirect("state")

def delete_state(request, id):
    state = get_object_or_404(State, id=id)
    if request.method == "POST":
        state.delete()
        return redirect("state")

def get_countries_ajax(request):
    """Return <option> list of active countries"""
    countries = Country.objects.filter(status=True).order_by("name")
    options = "".join([f'<option value="{c.id}">{c.name}</option>' for c in countries])
    return HttpResponse(options)
    

# City view

def city_view(request):
    if request.method == "POST":
        country_id = request.POST.get("country")
        state_id = request.POST.get("state")
        name = request.POST.get("name")
        if country_id and state_id and name:
            country = get_object_or_404(Country, id=country_id)
            state = get_object_or_404(State, id=state_id, country=country)
            City.objects.create(name=name, country=country, state=state)
        return redirect("city")
    return render(request, "city.html")

def get_city_details(request):
    """HTMX load city list, edit form, delete form"""
    if request.headers.get("HX-Request"):
        try:
            search = request.GET.get("q")
            get_edit = request.GET.get("get_edit")
            get_delete = request.GET.get("get_delete")

            if get_edit:
                city = get_object_or_404(City, id=get_edit)
                return render(request, "city/city_edit_form.html", {"city": city})

            if get_delete:
                city = get_object_or_404(City, id=get_delete)
                return render(request, "city/city_delete_form.html", {"city": city})

            if search:
                cities = City.objects.filter(Q(name__icontains=search))
            else:
                cities = City.objects.select_related("country", "state").order_by("-created_at")

            page_num = request.GET.get("page")
            paginator = Paginator(cities, 2)
            try:
                cities = paginator.page(page_num)
            except PageNotAnInteger:
                cities = paginator.page(1)
            except EmptyPage:
                cities = None

            return render(request, "city/city_list.html", {"cities": cities})
        except Exception as e:
            return HttpResponse(f"Error loading data: {str(e)}", e)
        
def edit_city(request, id):
    city = get_object_or_404(City, id=id)
    if request.method == "POST":
        country_id = request.POST.get("country")
        state_id = request.POST.get("state")
        name = request.POST.get("name")
        if country_id and state_id and name:
            country = get_object_or_404(Country, id=country_id)
            state = get_object_or_404(State, id=state_id, country=country)
            city.country = country
            city.state = state
            city.name = name
            city.save()
        return redirect("city")

def delete_city(request, id):
    city = get_object_or_404(City, id=id)
    if request.method == "POST":
        city.delete()
        return redirect("city")
    
def get_states_ajax(request, country_id):
    
    states = State.objects.filter(country_id=country_id, status=True).order_by("name")
    options = "".join([f'<option value="{s.id}">{s.name}</option>' for s in states])
    return HttpResponse(options)