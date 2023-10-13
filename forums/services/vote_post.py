from forums.models import ForumPost
from users.models import User


def upvote_post(post_id, user_id):
    post = ForumPost.objects.get(pk=post_id)
    user = User.objects.get(pk=user_id)

    if user in post.upvoters.all():
        post.vote_count -= 1
        post.upvoters.remove(user)
    elif user in post.downvoters.all():
        post.vote_count += 2
        post.downvoters.remove(user)
        post.upvoters.add(user)
    else:
        post.vote_count += 1
        post.upvoters.add(user)

    post.save()
    return post


def downvote_post(post_id, user_id):
    post = ForumPost.objects.get(pk=post_id)
    user = User.objects.get(pk=user_id)

    if user in post.downvoters.all():
        post.vote_count += 1
        post.downvoters.remove(user)
    elif user in post.upvoters.all():
        post.vote_count -= 2
        post.upvoters.remove(user)
        post.downvoters.add(user)
    else:
        post.vote_count -= 1
        post.downvoters.add(user)

    post.save()
    return post
