from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Country, State, City
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Q
from django.template.loader import render_to_string
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import csv
from xhtml2pdf import pisa   # for converting HTML → PDF
import io

from django.apps import apps

# Create your views here.
def home(request):
    return render(request, "home.html")


# Country view 

def country_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip().lower()

        if Country.objects.filter(name=name).exists():
            messages.error(request, "Country already exists!")
        else:
            Country.objects.create(name=name)
            messages.success(request, "Country added successfully!")
        return redirect("country")

    return render(request, "country.html")

def get_country_details(request):
    if request.headers.get('HX-Request'):
        try:
            search = request.GET.get('q')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')
            toggle_country_id = request.GET.get('toggle_country_id')
            
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
            # --- Toggle status request ---
            if toggle_country_id:
                country = get_object_or_404(Country, id=toggle_country_id)
                country.status = not country.status
                country.save()
                html = render_to_string("country/country_status.html", {"country": country})
                return HttpResponse(html)
            
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
        country = get_object_or_404(Country, id=id)
        name = request.POST.get('name', '').strip()
        try:
            country.name = name
            country.save()
            messages.success(request, "Country edited successfully!")
        except Exception as e:
            messages.error(request, f"Error updating country: {str(e)}")

        return redirect('country')

def delete_country(request, id):
    try:
        country = get_object_or_404(Country, id=id)

        if request.method == "POST":
            country.delete()   # ✅ fixed
            messages.success(request, "country deleted successfully!")
            return redirect('country')

    except Exception as e:
        messages.error(request, f"Error deleting country: {str(e)}")
        return redirect('country')



# State view

def state_view(request):
    if request.method == "POST":
        country_id = request.POST.get("country")
        name = request.POST.get("name", "").strip().lower()
        if State.objects.filter(name=name).exists():
            messages.error(request, "State already exists!")
        
        if country_id and name:
            country = get_object_or_404(Country, id=country_id)
            print(country)
            State.objects.create(name=name, country=country)
            messages.success(request, "State added successfully!")
        return redirect("state")
    return render(request, 'state.html')


def get_state_details(request):
    """HTMX load state list"""
    if request.headers.get('HX-Request'):
        
        try:
            search = request.GET.get('q')
            get_edit = request.GET.get('get_edit')
            get_delete = request.GET.get('get_delete')
            toggle_state_id = request.GET.get('toggle_state_id')
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
            
             # --- Toggle status request ---
            if toggle_state_id:
                state = get_object_or_404(Country, id=toggle_state_id)
                state.status = not state.status
                state.save()
                html = render_to_string("state/state_status.html", {"state": state})
                return HttpResponse(html)
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
         # check duplicate (exclude current record)
        if State.objects.filter(country_id=country_id, name__iexact=name).exclude(id=state.id).exists():
            messages.error(request, "State already exists for the selected country.")
            return redirect("state")
        if country_id and name:
            country = get_object_or_404(Country, id=country_id)
            state.country = country
            state.name = name
            state.save()
            messages.success(request, "State edited successfully!")
        return redirect("state")

def delete_state(request, id):
    state = get_object_or_404(State, id=id)
    if request.method == "POST":
        state.delete()
        messages.success(request, "state deleted successfully!")
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
        name = request.POST.get("name", "").strip().lower()
        if City.objects.filter(name=name).exists():
            messages.error(request, "City already exists!")
        else:
            if country_id and state_id and name:
                country = get_object_or_404(Country, id=country_id)
                state = get_object_or_404(State, id=state_id, country=country)
                City.objects.create(name=name, country=country, state=state)
                messages.success(request, "City added successfully!")
        return redirect("city")
    return render(request, "city.html")

def get_city_details(request):
    """HTMX load city list, edit form, delete form"""
    if request.headers.get("HX-Request"):
        try:
            search = request.GET.get("q")
            get_edit = request.GET.get("get_edit")
            get_delete = request.GET.get("get_delete")
            toggle_city_id = request.GET.get('toggle_city_id')
            if get_edit:
                city = get_object_or_404(City, id=get_edit)
                return render(request, "city/city_edit_form.html", {"city": city})

            if get_delete:
                city = get_object_or_404(City, id=get_delete)
                return render(request, "city/city_delete_form.html", {"city": city})

            # --- Toggle status request ---
            if toggle_city_id:
                city = get_object_or_404(City, id=toggle_city_id)
                city.status = not city.status
                city.save()
                html = render_to_string("city/city_status.html", {"city": city})
                return HttpResponse(html)
            
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
            messages.success(request, "City edited successfully!")
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


@require_POST
def ajax_check_state_unique(request):
    """
    POST: name, country, id (optional - current record id)
    Returns JSON: { valid: true } or { valid: false, message: "..." }
    """
    name = request.POST.get("name", "").strip()
    country_id = request.POST.get("country")
    current_id = request.POST.get("id")

    # if missing inputs, treat as valid so 'required' handles empties client-side
    if not name or not country_id:
        return JsonResponse({"valid": True})

    qs = State.objects.filter(country_id=country_id, name__iexact=name)
    if current_id:
        qs = qs.exclude(id=current_id)

    if qs.exists():
        return JsonResponse({
            "valid": False,
            "message": "This state already exists for the selected country."
        })
    return JsonResponse({"valid": True})


def validate_city_edit(request):
    country_id = request.GET.get("country")
    state_id = request.GET.get("state")
    name = request.GET.get("name", "").strip()
    city_id = request.GET.get("city_id")  # current editing city

    exists = City.objects.filter(
        country_id=country_id,
        state_id=state_id,
        name__iexact=name
    ).exclude(id=city_id).exists()

    return JsonResponse(not exists, safe=False)  

# Export view 
def export_records(request, model_name):
    # Dynamically get the model (Country, State, City)
    Model = apps.get_model('area', model_name)

    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")
    export_format = request.GET.get("format")  # new dropdown field

    queryset = Model.objects.all().order_by("-id")

    # filter by date range if both provided
    if from_date and to_date:
        queryset = queryset.filter(created_at__date__range=[from_date, to_date])

    # 🔹 If no records found → show error and go back
    if not queryset.exists():
        messages.error(request, "No records present in this date range.")
        return redirect(request.META.get("HTTP_REFERER", f"/{model_name.lower()}/"))

    # ✅ CSV Export
    if export_format == "csv":
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = f'attachment; filename="{model_name.lower()}_records.csv"'
        writer = csv.writer(response)

        # headers
        fields = [f.name for f in Model._meta.fields if not f.primary_key]
        writer.writerow(["Sl. No."] + fields)

        # rows
        for idx, obj in enumerate(queryset, start=1):
            row = [getattr(obj, field) for field in fields]
            writer.writerow([idx] + row)

        return response

    # ✅ PDF Export using HTML template
    elif export_format == "pdf":
        # Select template based on model
        template_name = f"{model_name.lower()}/{model_name.lower()}_pdf.html"

        # Prepare context
        fields = [field.name for field in Model._meta.fields]
        context = {
            "model_name": model_name,
            "fields": fields,
            "records": queryset,
        }

        # Render HTML template
        html = render_to_string(template_name, context)

        # Convert HTML to PDF
        response = HttpResponse(content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{model_name.lower()}_records.pdf"'

        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse("Error generating PDF", status=500)

        return response

    else:
        messages.error(request, "Please select a valid export format.")
        return redirect(request.META.get("HTTP_REFERER", f"/{model_name.lower()}/"))