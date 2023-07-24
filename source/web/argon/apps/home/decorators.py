from django.shortcuts import render

# Decorator to only allow POST requests only
def post_request_only (view_func):
    def wrapper_func(request, *args, **kwargs):

        # Check if the request method is correct
        if (request.method != "POST"):
            # Redirect user to the error page
            return render(request, "home/page-404.html") 
        else:
            # Pass control to view
            return view_func(request, *args, **kwargs)

    return wrapper_func