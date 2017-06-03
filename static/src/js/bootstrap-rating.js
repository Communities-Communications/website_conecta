! function(t, i) {
    "use strict";

    function n(n, o) {
        this.$input = t(n), this.$rating = t("<span></span>").css({
            cursor: "default"
        }).insertBefore(this.$input), this.options = function(n) {
            return n.start = parseInt(n.start, 10), n.start = isNaN(n.start) ? i : n.start, n.stop = parseInt(n.stop, 10), n.stop = isNaN(n.stop) ? n.start + s || i : n.stop, n.step = parseInt(n.step, 10) || i, n.fractions = Math.abs(parseInt(n.fractions, 10)) || i, n.scale = Math.abs(parseInt(n.scale, 10)) || i, n = t.extend({}, t.fn.rating.defaults, n), n.filledSelected = n.filledSelected || n.filled, n
        }(t.extend({}, this.$input.data(), o)), this._init()
    }
    var s = 5;
    n.prototype = {
        _init: function() {
            for (var n = this, s = this.$input, o = this.$rating, a = function(t) {
                    return function(n) {
                        s.prop("disabled") || s.prop("readonly") || s.data("readonly") !== i || t.call(this, n)
                    }
                }, e = 1; e <= this._rateToIndex(this.options.stop); e++) {
                var r = t('<div class="rating-symbol"></div>').css({
                    display: "inline-block",
                    position: "relative"
                });
                t('<div class="rating-symbol-background ' + this.options.empty + '"></div>').appendTo(r), t('<div class="rating-symbol-foreground"></div>').append("<span></span>").css({
                    display: "inline-block",
                    position: "absolute",
                    overflow: "hidden",
                    left: 0,
                    right: 0,
                    width: 0
                }).appendTo(r), o.append(r), this.options.extendSymbol.call(r, this._indexToRate(e))
            }
            this._updateRate(s.val()), s.on("change", function() {
                n._updateRate(t(this).val())
            });
            var l, p = function(i) {
                var s = t(i.currentTarget),
                    o = Math.abs((i.pageX || i.originalEvent.touches[0].pageX) - (("rtl" === s.css("direction") && s.width()) + s.offset().left));
                return o = o > 0 ? o : .1 * n.options.scale, s.index() + o / s.width()
            };
            o.on("mousedown touchstart", ".rating-symbol", a(function(t) {
                s.val(n._indexToRate(p(t))).change()
            })).on("mousemove touchmove", ".rating-symbol", a(function(s) {
                var o = n._roundToFraction(p(s));
                o !== l && (l !== i && t(this).trigger("rating.rateleave"), l = o, t(this).trigger("rating.rateenter", [n._indexToRate(l)])), n._fillUntil(o)
            })).on("mouseleave touchend", ".rating-symbol", a(function() {
                l = i, t(this).trigger("rating.rateleave"), n._fillUntil(n._rateToIndex(parseFloat(s.val())))
            }))
        },
        _fillUntil: function(t) {
            var i = this.$rating,
                n = Math.floor(t);
            i.find(".rating-symbol-background").css("visibility", "visible").slice(0, n).css("visibility", "hidden");
            var s = i.find(".rating-symbol-foreground");
            s.width(0), s.slice(0, n).width("auto").find("span").attr("class", this.options.filled), s.eq(t % 1 ? n : n - 1).find("span").attr("class", this.options.filledSelected), s.eq(n).width(t % 1 * 100 + "%")
        },
        _indexToRate: function(t) {
            return this.options.start + Math.floor(t) * this.options.step + this.options.step * this._roundToFraction(t % 1)
        },
        _rateToIndex: function(t) {
            return (t - this.options.start) / this.options.step
        },
        _roundToFraction: function(t) {
            var i = Math.ceil(t % 1 * this.options.fractions) / this.options.fractions,
                n = Math.pow(10, this.options.scale);
            return Math.floor(t) + Math.floor(i * n) / n
        },
        _contains: function(t) {
            var i = this.options.step > 0 ? this.options.start : this.options.stop,
                n = this.options.step > 0 ? this.options.stop : this.options.start;
            return t >= i && n >= t
        },
        _updateRate: function(t) {
            var i = parseFloat(t);
            this._contains(i) && (this._fillUntil(this._rateToIndex(i)), this.$input.val(i))
        },
        rate: function(t) {
            return t === i ? this.$input.val() : void this._updateRate(t)
        }
    }, t.fn.rating = function(i) {
        var s, o = Array.prototype.slice.call(arguments, 1);
        return this.each(function() {
            var a = t(this),
                e = a.data("rating");
            e || a.data("rating", e = new n(this, i)), "string" == typeof i && "_" !== i[0] && (s = e[i].apply(e, o))
        }), s || this
    }, t.fn.rating.defaults = {
        filled: "glyphicon glyphicon-star",
        filledSelected: i,
        empty: "glyphicon glyphicon-star-empty",
        start: 0,
        stop: s,
        step: 1,
        fractions: 1,
        scale: 3,
        extendSymbol: function(t) {}
    }, t(function() {
        t("input.rating").rating()
    })
}(jQuery);
