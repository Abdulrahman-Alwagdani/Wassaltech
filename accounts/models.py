from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Avg, F


# Create your models here.
def user_avatar_path(instance, filename):
    return f'avatars/{instance.user.username}/{filename}'


class Account(models.Model):
    avatar = models.ImageField(upload_to=user_avatar_path, default='avatars/default_profile.png', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.user.first_name} {self.user.last_name}"


def user_certificate_path(instance, filename):
    return f'certificates/{instance.user.username}/{filename}'


class Freelancer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=100)
    certificate_expiration = models.DateField(blank=True, null=True)
    certificate_image = models.ImageField(upload_to=user_certificate_path)
    internal_rating = models.FloatField(default=10, validators=[MinValueValidator(0), MaxValueValidator(10)])
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-internal_rating']

    def __str__(self):
        return f"{self.user.username} | Is Verified: {self.is_verified}"

    def get_completion_count(self) -> int:
        """
        Calculate the number of offers associated with this freelancer that are in the 'Completed' stage.

        Returns:
            int: The count of offers in the 'Completed' stage.
        """
        completion_count = self.offer_set.filter(stage='Completed').count() or 0
        return completion_count

    def get_cancellation_count(self) -> int:
        """
        Calculate the number of offers associated with this freelancer that are in the 'Cancelled' stage.

        Returns:
            int: The count of offers in the 'Cancelled' stage.
        """
        cancellation_count = self.offer_set.filter(stage='Cancelled').count() or 0
        return cancellation_count

    def get_completion_rate(self) -> float:
        """
        Calculate the completion rate for this freelancer.

        Completion rate is defined as the ratio of completed offers to the sum of completed and cancelled offers.
        If no offers have been completed or cancelled, the rate is set to 1 (100%).

        Returns:
            float: The completion rate of the freelancer.
        """
        if self.offer_set.filter(Q(stage='Completed') | Q(stage='Cancelled')).exists() is False:
            return 1
        completion_rate = self.get_completion_count() / (self.get_completion_count() + self.get_cancellation_count())
        return completion_rate

    def get_timely_completion_count(self) -> int:
        """
        Calculate the number of offers completed on time by this freelancer.

        Returns:
            int: The count of offers completed on time.
        """
        timely_completion_count = self.offer_set.filter(stage='Completed', complete_on_time=True).count()
        return timely_completion_count

    def get_success_rate(self) -> float:
        """
        Calculate the success rate for this freelancer.

        Success rate is defined as the ratio of offers completed on time to the total number of completed offers.
        If no offers have been completed, the rate is set to 1 (100%).

        Returns:
            float: The success rate of the freelancer.
        """
        if self.offer_set.filter(stage='Completed').exists() is False:
            return 1
        success_rate = self.get_timely_completion_count() / self.get_completion_count()
        return success_rate

    def get_freelancer_rating(self) -> float:
        """
        Calculate the average rating for this freelancer.

        Freelancer rating is defined as the average of review ratings for completed offers, normalized to a scale of 1.
        If no offers have been completed, the rating is set to 1.

        Returns:
            float: The average rating of the freelancer.
        """
        if self.offer_set.filter(stage='Completed').exists() is False:
            return 1
        average_rating = self.offer_set.annotate(rating=F('review__rating')).aggregate(avg_rating=Avg('rating'))[
            'avg_rating']
        freelancer_rating = average_rating / 5
        return freelancer_rating

    def update_internal_rating(self) -> None:
        """
        Update the internal rating of the freelancer.

        The internal rating is calculated as a weighted sum of the completion rate, success rate, and freelancer rating:
        - 30% for completion rate
        - 40% for success rate
        - 30% for freelancer rating

        The internal rating is then saved to the database.

        Returns:
            None
        """
        self.internal_rating = 0.3 * self.get_completion_rate() + 0.4 * self.get_success_rate() + 0.3 * self.get_freelancer_rating()
        self.save()
