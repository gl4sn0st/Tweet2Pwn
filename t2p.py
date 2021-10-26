from TwitterAPI import TwitterAPI
import json

api = TwitterAPI("ypR4UyFZwOExNuSHk5yY1HBxL", "imE9YwcSIQDVnaf4VGWlfm0zT0191wnME07lPm42uQ6UkPRdpu", "1452730066190876679-mfGkF2fQAZpZAB95EavXDQVfh4jhGe", "lkldhBWdxcZ6UZVeSx2ohpvLTzjQwCJG0JYHFheLc1bsH")

r = api.request("direct_messages/events/list")
print(r.text)
