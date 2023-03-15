from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Review
from app.classes.forms import ReviewForm
from flask_login import login_required
import datetime as dt


@app.route('/review/list')
@app.route('/reviews')

@login_required
def ReviewList():
    reviews = Review.objects()
    return render_template('reviews.html',reviews = reviews)

@app.route('/review/<reviewID>')

@login_required
def review(reviewID):
    # retrieve the review using the reviewID
    thisReview = Review.objects.get(id=reviewID)
    # If there are no comments the 'comments' object will have the value 'None'. Comments are 
    # related to reviews meaning that every comment contains a reference to a review. In this case
    # there is a field on the comment collection called 'review' that is a reference the Review
    # document it is related to.  You can use the reviewID to get the review and then you can use
    # the review object (thisReview in this case) to get all the comments.
    # Send the review object and the comments object to the 'review.html' template.
    return render_template('review.html',review=thisReview)


@app.route('/review/delete/<reviewID>')
# Only run this route if the user is logged in.
@login_required
def reviewDelete(reviewID):
    # retrieve the review to be deleted using the reviewID
    deleteReview = Review.objects.get(id=reviewID)
    # check to see if the user that is making this request is the author of the review.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteReview.author:
        # delete the review using the delete() method from Mongoengine
        deleteReview.delete()
        # send a message to the user that the review was deleted.
        flash('The Review was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a review you don't own.")
    # Retrieve all of the remaining reviews so that they can be listed.
    reviews = Review.objects()  
    # Send the user to the list of remaining reviews.
    return render_template('reviews.html',reviews=reviews)


@app.route('/review/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def reviewNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = ReviewForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new review form. 
        # Review() is a mongoengine method for creating a new review. 'newReview' is the variable 
        # that stores the object that is the result of the Review() method.  
        newReview= Review(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            star = form.star.data,
            text = form.text.data,
            recommendation = form.recommendation.data,
            author = current_user.id,
            
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newReview.save()

        # Once the new review is saved, this sends the user to that review using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a review so we want 
        # to send them to that review. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('review',reviewID=newReview.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at reviewform.html to 
    # see how that works.
    return render_template('reviewform.html', form=form)


@app.route('/review/edit/<reviewID>', methods=['GET', 'POST'])
@login_required
def reviewEdit(reviewID):
    editReview = Review.objects.get(id=reviewID)
    # if the user that requested to edit this review is not the author then deny them and
    # send them back to the review. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editReview.author:
        flash("You can't edit a review you don't own.")
        return redirect(url_for('review',reviewID=reviewID))
    # get the form object
    form = ReviewForm()
    # If the user has submitted the form then update the review.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editReview.update(
            star = form.star.data,
            recommendation = form.recommendation.data,
            text = form.text.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated review using a redirect.
        return redirect(url_for('review',reviewID=reviewID))

    # if the form has NOT been submitted then take the data from the editReview object
    # and place it in the form object so it will be displayed to the user on the template.
    form.star.data = editReview.star
    form.text.data = editReview.text
    form.recommendation.data = editReview.recommendation
    


    # Send the user to the review form that is now filled out with the current information
    # from the form.
    return render_template('reviewform.html',form=form)